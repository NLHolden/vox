"""Build video clips that match still and animated art to speech segments."""

from __future__ import annotations

import librosa
import numpy as np
from moviepy.editor import ImageClip, VideoFileClip
from moviepy.video.VideoClip import VideoClip


class SoundSynchronizer:
    """Create a sequence of static and animated clips from a spoken audio file."""

    frame_length = 2048
    hop_length = 512
    talk_padding = 0.1

    def __init__(
        self,
        wav_filename: str,
        animation_filename: str,
        end_animation_file: str,
        static_image: str,
    ) -> None:
        self.wav_filename = wav_filename
        self.first_animation = VideoFileClip(animation_filename)
        self.final_animation = VideoFileClip(end_animation_file)
        self.static_image = static_image

    def get_talking_segments(self) -> list[tuple[float, float]]:
        """Return start and end times for speech-like audio segments."""
        audio, sample_rate = librosa.load(self.wav_filename, sr=None)
        energy = librosa.feature.rms(
            y=audio,
            frame_length=self.frame_length,
            hop_length=self.hop_length,
        )[0]

        threshold = np.median(energy) * 1.5
        talking = energy > threshold
        times = librosa.frames_to_time(
            np.arange(len(energy)),
            sr=sample_rate,
            hop_length=self.hop_length,
        )

        segments: list[tuple[float, float]] = []
        in_segment = False
        for index, is_talking in enumerate(talking):
            if is_talking and not in_segment:
                start = float(times[index])
                in_segment = True
            elif not is_talking and in_segment:
                end = float(times[index])
                segments.append((start, end))
                in_segment = False

        if in_segment:
            segments.append((start, float(times[-1])))

        return segments

    def produce_static_clip(self, duration_seconds: float) -> VideoClip:
        """Create a still-image clip with the requested duration."""
        return ImageClip(self.static_image).set_duration(duration_seconds).set_fps(24)

    def fit_animation_to_segment(self, duration_seconds: float) -> list[VideoClip]:
        """Fit looping and closing animations to one speech segment."""
        num_clips = int(duration_seconds / self.first_animation.duration)
        over_time = (
            num_clips * self.first_animation.duration
            + self.final_animation.duration
            - duration_seconds
        )

        adjustment = over_time / (num_clips + 1)
        first_duration = self.first_animation.duration - adjustment
        first_speed = self.first_animation.duration / first_duration
        faster_clip = self.first_animation.speedx(factor=first_speed)

        final_duration = self.final_animation.duration - adjustment
        final_speed = self.final_animation.duration / final_duration
        faster_final_clip = self.final_animation.speedx(factor=final_speed)

        assert np.isclose(
            faster_clip.duration * num_clips + faster_final_clip.duration,
            duration_seconds,
            0.05,
        )
        return [faster_clip for _ in range(num_clips)] + [faster_final_clip]

    def wav_file_duration_seconds(self) -> float:
        """Return the input audio duration in seconds."""
        audio, sample_rate = librosa.load(self.wav_filename, sr=None)
        return len(audio) / sample_rate

    def get_video_output(self) -> list[VideoClip]:
        """Create the still and animation clips in timeline order."""
        talk_segments = self.get_talking_segments()
        previous_segment_end = 0.0
        clips: list[VideoClip] = []

        for start, finish in talk_segments:
            clips.append(self.produce_static_clip(start - previous_segment_end))
            clips.extend(
                self.fit_animation_to_segment(self.talk_padding + finish - start)
            )
            previous_segment_end = finish + self.talk_padding

        clips.append(
            self.produce_static_clip(
                self.wav_file_duration_seconds() - previous_segment_end
            )
        )
        return clips
