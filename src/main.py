import librosa
from moviepy.editor import ImageClip, VideoFileClip, concatenate_videoclips, vfx
from moviepy.video.fx.speedx import speedx


import numpy as np

class SoundSynchronizer:
    def __init__(self, wav_filename : str, animation_filename : str, end_animation_file : str, static_image : str) -> None:
        self.wav_filenae = wav_filename
        self.first_animation = VideoFileClip(animation_filename)
        self.final_animation = VideoFileClip(end_animation_file)

        self.static_image = static_image

        self.FRAME_LENGTH = 2048
        self.HOP_LENGTH = 512

    def get_talking_segments(self) -> list[float, float]:
        y, sr = librosa.load(self.wav_filenae, sr=None)

        energy = librosa.feature.rms(y=y, frame_length=self.FRAME_LENGTH, hop_length=self.HOP_LENGTH)[0]

        threshold = np.median(energy) * 1.5
        talking = energy > threshold

        times = librosa.frames_to_time(np.arange(len(energy)), sr=sr, hop_length=self.HOP_LENGTH)

        segments = []
        in_segment = False
        for i, is_talking in enumerate(talking):
            if is_talking and not in_segment:
                start = times[i]
                in_segment = True
            elif not is_talking and in_segment:
                end = times[i]
                segments.append((start, end))
                in_segment = False
        if in_segment:
            segments.append((start, times[-1]))

        return segments

    def produce_static_clip(self, duration_seconds : float) -> VideoFileClip:
        clip = ImageClip(self.static_image).set_duration(duration_seconds).set_fps(24)

        return clip

    def fit_animation_to_segment(self, duration_seconds : float) -> list[VideoFileClip]:
        num_clips = int(duration_seconds / self.first_animation.duration)

        over_time = num_clips * self.first_animation.duration + self.final_animation.duration - duration_seconds

        new_duration_first_clip = self.first_animation.duration - over_time / (num_clips+1)

        speed_up_factor = self.first_animation.duration / new_duration_first_clip

        faster_clip = self.first_animation.speedx(factor=speed_up_factor)

        new_duration_final_clip = self.final_animation.duration - over_time / (num_clips + 1)

        speed_up_factor_final = self.final_animation.duration / new_duration_final_clip

        faster_clip_final = self.final_animation.speedx(factor=speed_up_factor_final)

        assert np.isclose(faster_clip.duration * num_clips + faster_clip_final.duration, duration_seconds, 0.05)

        return [faster_clip for _ in range(num_clips)] + [faster_clip_final]

    def wav_file_duration_seconds(self) -> float:
        y, sr = librosa.load(self.wav_filenae, sr=None)

        return len(y) / sr

    def get_video_output(self) -> VideoFileClip:
        talk_segments = self.get_talking_segments()

        prev_segment = 0
        clips = []

        TALK_PADDING = 0.1

        for start, finish in talk_segments:
            clips.append(self.produce_static_clip(start - prev_segment))

            clips += self.fit_animation_to_segment(TALK_PADDING + finish - start)

            prev_segment = finish + TALK_PADDING

        clips.append(self.produce_static_clip(self.wav_file_duration_seconds() - prev_segment))

        return clips

syncer = SoundSynchronizer(wav_filename='../episode0-introduction/episode0_audio_pitched.wav', animation_filename='graphics/Holden_talking_half_open.mp4', end_animation_file='graphics/Holden_talking_full.mp4', static_image='graphics/Holden_Final.png')

clips = syncer.get_video_output()

final_clip = concatenate_videoclips(clips)

final_clip.write_videofile("episode0.mp4", codec='libx264')
