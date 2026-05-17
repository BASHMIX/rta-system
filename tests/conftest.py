import json
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest

from src.config.models import GameProfile, SystemConfig, PlayerConfig, ROIConfig, OBSEvent, OBSAction


@pytest.fixture
def temp_profiles_dir() -> Generator[Path, None, None]:
    tmp_dir = Path(tempfile.mkdtemp())
    yield tmp_dir
    shutil.rmtree(tmp_dir)


@pytest.fixture
def sample_profile() -> GameProfile:
    return GameProfile(
        name="Street Fighter 6",
        system=SystemConfig(
            resolution=[1920, 1080],
            target_fps=30,
        ),
        players={
            "P1": PlayerConfig(
                lifebar=ROIConfig(
                    roi=[100, 50, 800, 80],
                    direction="RTL",
                    segments=4,
                    target_color_hsv_range=[[40, 50, 50], [80, 255, 255]],
                ),
                system_text_zone=ROIConfig(
                    roi=[100, 300, 400, 350],
                    direction="LTR",
                    segments=1,
                    target_color_hsv_range=[[0, 0, 0], [180, 255, 255]],
                ),
            ),
            "P2": PlayerConfig(
                lifebar=ROIConfig(
                    roi=[1120, 50, 1820, 80],
                    direction="LTR",
                    segments=4,
                    target_color_hsv_range=[[40, 50, 50], [80, 255, 255]],
                ),
            ),
        },
        obs_events=[
            OBSEvent(
                trigger="P1_Life_Under_25",
                condition="P1.lifebar.current_percentage < 25",
                actions=[
                    OBSAction(type="toggle_source", scene="Main_Gameplay", source="Red_Danger_Vignette", state=True),
                ],
            ),
        ],
    )


@pytest.fixture
def sample_profile_dict(sample_profile: GameProfile) -> dict:
    return sample_profile.to_dict()


@pytest.fixture
def setup_profiles_dir(temp_profiles_dir: Path, sample_profile: GameProfile) -> Path:
    profile_path = temp_profiles_dir / "street-fighter-6.json"
    with open(profile_path, "w") as f:
        json.dump(sample_profile.to_dict(), f, indent=2)
    index_path = temp_profiles_dir / "index.json"
    index_data = {
        "profiles": [
            {
                "name": sample_profile.name,
                "created_at": sample_profile.created_at,
                "updated_at": sample_profile.updated_at,
                "game_summary": "3 ROIs, 1 event",
            }
        ],
        "last_loaded": sample_profile.name,
    }
    with open(index_path, "w") as f:
        json.dump(index_data, f, indent=2)
    return temp_profiles_dir
