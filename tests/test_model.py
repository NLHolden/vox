import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from model import VoxConfig


@pytest.fixture
def config_data() -> dict[str, str]:
    return {
        "static_image_filename": "assets/images/holden.png",
        "animation_filename": "assets/graphics/talking.mp4",
        "end_animation_filename": "assets/graphics/closing.mp4",
    }


def test_parse_config_json(config_data: dict[str, str]) -> None:
    config = VoxConfig.model_validate_json(json.dumps(config_data))

    assert config.static_image_filename == Path(config_data["static_image_filename"])
    assert config.animation_filename == Path(config_data["animation_filename"])
    assert config.end_animation_filename == Path(config_data["end_animation_filename"])


def test_serialize_and_parse_config(config_data: dict[str, str]) -> None:
    config = VoxConfig.model_validate(config_data)

    serialized = config.model_dump_json()
    restored = VoxConfig.model_validate_json(serialized)

    assert restored == config
    serialized_paths = {key: str(Path(value)) for key, value in config_data.items()}
    assert json.loads(serialized) == serialized_paths


@pytest.mark.parametrize(
    "missing_field",
    [
        "static_image_filename",
        "animation_filename",
        "end_animation_filename",
    ],
)
def test_parse_config_requires_all_asset_paths(
    config_data: dict[str, str], missing_field: str
) -> None:
    incomplete_config = config_data.copy()
    del incomplete_config[missing_field]

    with pytest.raises(ValidationError):
        VoxConfig.model_validate(incomplete_config)


def test_parse_config_rejects_unknown_fields(config_data: dict[str, str]) -> None:
    config_data["unexpected"] = "value"

    with pytest.raises(ValidationError):
        VoxConfig.model_validate(config_data)


def test_parse_config_rejects_invalid_json() -> None:
    with pytest.raises(ValidationError):
        VoxConfig.model_validate_json("{not valid json}")
