import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_videoclips
from pydantic import ValidationError

from model import VoxConfig
from sound_synchronizer import SoundSynchronizer

LOGGER = logging.getLogger("vox")


def _load_config(config_path: Path) -> VoxConfig:
    """Load the JSON config and resolve its asset paths relative to the file."""
    try:
        config = VoxConfig.model_validate_json(config_path.read_text(encoding="utf-8"))
    except ValidationError as exc:
        raise ValueError(f"invalid configuration in {config_path}:\n{exc}") from exc
    except (OSError, UnicodeError) as exc:
        raise ValueError(
            f"could not read configuration file {config_path}: {exc}"
        ) from exc

    config_dir = config_path.resolve().parent
    for field_name in (
        "static_image_filename",
        "animation_filename",
        "end_animation_filename",
    ):
        asset_path = getattr(config, field_name)
        if not asset_path.is_absolute():
            asset_path = config_dir / asset_path
        asset_path = asset_path.resolve()
        if not asset_path.is_file():
            raise ValueError(f"configured asset does not exist: {asset_path}")
        setattr(config, field_name, asset_path)

    return config


def _close_clips(clips: Sequence[object]) -> None:
    closed: set[int] = set()
    for clip in clips:
        clip_id = id(clip)
        close = getattr(clip, "close", None)
        if clip_id not in closed and callable(close):
            close()
            closed.add(clip_id)


def run_vox(config_path: Path, audio_path: Path, output_path: Path) -> None:
    """Render one audio file to an MP4 using a Vox JSON configuration."""
    config_path = config_path.expanduser()
    audio_path = audio_path.expanduser()
    output_path = output_path.expanduser()

    if not config_path.is_file():
        raise ValueError(f"configuration file does not exist: {config_path}")
    if not audio_path.is_file():
        raise ValueError(f"audio file does not exist: {audio_path}")
    if output_path.suffix.lower() != ".mp4":
        raise ValueError("output file must have an .mp4 extension")

    config = _load_config(config_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    synchronizer: SoundSynchronizer | None = None
    clips: list[VideoFileClip] = []
    final_clip: Any | None = None
    audio_clip: AudioFileClip | None = None
    try:
        synchronizer = SoundSynchronizer(
            wav_filename=str(audio_path.resolve()),
            animation_filename=str(config.animation_filename),
            end_animation_file=str(config.end_animation_filename),
            static_image=str(config.static_image_filename),
        )
        clips = synchronizer.get_video_output()
        if not clips:
            raise ValueError("the synchronizer did not produce any video clips")

        final_clip = concatenate_videoclips(clips)
        audio_clip = AudioFileClip(str(audio_path.resolve()))
        final_clip = final_clip.set_audio(audio_clip)
        LOGGER.info("Rendering %s", output_path)
        final_clip.write_videofile(str(output_path), codec="libx264", audio=True)
        LOGGER.info("Created %s", output_path.resolve())
    finally:
        owned_clips: list[object] = []
        if final_clip is not None:
            owned_clips.append(final_clip)
        if audio_clip is not None:
            owned_clips.append(audio_clip)
        owned_clips.extend(clips)
        if synchronizer is not None:
            owned_clips.extend(
                [synchronizer.first_animation, synchronizer.final_animation]
            )
        _close_clips(owned_clips)
