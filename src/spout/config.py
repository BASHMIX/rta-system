from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    pass


@dataclass
class SpoutConfig:
    sender_name: str = "OBS"
    sample_points: list[tuple[int, int]] = field(default_factory=lambda: [(100, 100)])
    target_fps: int = 30

    @classmethod
    def from_file(cls, path: str | Path) -> "SpoutConfig":
        p = Path(path)
        if not p.is_file():
            raise ConfigError(f"config.json not found at {p.resolve()}")
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ConfigError(f"Failed to parse config.json: {e}")
        if "spout" not in raw:
            raise ConfigError("config.json missing required top-level key 'spout'")
        sp = raw["spout"]
        sender_name = sp.get("sender_name", "OBS")
        if not isinstance(sender_name, str) or not sender_name.strip():
            raise ConfigError("spout.sender_name must be a non-empty string")
        raw_points = sp.get("sample_points", [(100, 100)])
        if not isinstance(raw_points, list) or len(raw_points) == 0:
            raise ConfigError("spout.sample_points must contain at least one [x, y] pair")
        points: list[tuple[int, int]] = []
        for i, pt in enumerate(raw_points):
            if not isinstance(pt, list) or len(pt) != 2:
                raise ConfigError(
                    f"spout.sample_points[{i}]: expected [x, y] pair of integers"
                )
            x, y = pt
            if not isinstance(x, int) or not isinstance(y, int):
                raise ConfigError(
                    f"spout.sample_points[{i}]: expected [x, y] pair of integers"
                )
            if x < 0 or y < 0:
                raise ConfigError(
                    f"spout.sample_points[{i}]: x and y must be non-negative"
                )
            points.append((x, y))
        target_fps = sp.get("target_fps", 30)
        if not isinstance(target_fps, int) or target_fps < 1 or target_fps > 240:
            raise ConfigError(
                f"spout.target_fps must be 1–240 (got {target_fps})"
            )
        logger.info(
            "Loaded Spout config: sender='%s', %d points, %d FPS",
            sender_name,
            len(points),
            target_fps,
        )
        return cls(sender_name=sender_name, sample_points=points, target_fps=target_fps)
