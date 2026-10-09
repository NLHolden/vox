from pathlib import Path

from pydantic import BaseModel, ConfigDict


class VoxConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    static_image_filename: Path
    animation_filename: Path
    end_animation_filename: Path
