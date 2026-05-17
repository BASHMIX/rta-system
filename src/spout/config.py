from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from src.roi import ROI

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    pass


@dataclass
class SpoutConfig:
    sender_name: str = "OBS"
    sample_points: list[tuple[int, int]] = field(default_factory=lambda: [(100, 100)])
    target_fps: int = 30
    rois: list[ROI] = field(default_factory=list)
    obs_host: str = "127.0.0.1"
    obs_port: int = 4455
    frame_skip: int = 2

    @classmethod
    def from_file(cls, path: str | Path) -> "SpoutConfig":
        p = Path(path)
        if not p.is_file():
            raise ConfigError(f"config.json not found at {p.resolve()}")
        try:
            raw = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ConfigError(f"Failed to parse config.json: {e}")

        sp = raw.get("spout", {})
        sender_name = sp.get("sender_name", "OBS")
        if not isinstance(sender_name, str) or not sender_name.strip():
            raise ConfigError("spout.sender_name must be a non-empty string")

        raw_points = sp.get("sample_points", [(100, 100)])
        points: list[tuple[int, int]] = []
        for i, pt in enumerate(raw_points):
            if not isinstance(pt, list) or len(pt) != 2:
                raise ConfigError(f"spout.sample_points[{i}]: expected [x, y] pair")
            x, y = pt
            if not isinstance(x, int) or not isinstance(y, int):
                raise ConfigError(f"spout.sample_points[{i}]: expected integers")
            points.append((x, y))

        target_fps = sp.get("target_fps", 30)
        if not isinstance(target_fps, int) or target_fps < 1 or target_fps > 240:
            raise ConfigError(f"spout.target_fps must be 1-240 (got {target_fps})")

        raw_rois = raw.get("rois", [])
        rois = [ROI.from_dict(r) for r in raw_rois]

        obs = raw.get("obs", {})
        obs_host = obs.get("host", "127.0.0.1")
        obs_port = obs.get("port", 4455)

        frame_skip = raw.get("frame_skip", 2)
        if not isinstance(frame_skip, int) or frame_skip < 0 or frame_skip > 10:
            raise ConfigError(f"frame_skip must be 0-10 (got {frame_skip})")

        logger.info(
            "Loaded config: sender='%s', %d points, %d FPS, %d ROIs, skip=%d",
            sender_name,
            len(points),
            target_fps,
            len(rois),
            frame_skip,
        )
        return cls(
            sender_name=sender_name,
            sample_points=points,
            target_fps=target_fps,
            rois=rois,
            obs_host=obs_host,
            obs_port=obs_port,
            frame_skip=frame_skip,
        )

    def to_dict(self) -> dict:
        return {
            "spout": {
                "sender_name": self.sender_name,
                "sample_points": [list(p) for p in self.sample_points],
                "target_fps": self.target_fps,
            },
            "obs": {
                "host": self.obs_host,
                "port": self.obs_port,
            },
            "rois": [r.to_dict() for r in self.rois],
            "frame_skip": self.frame_skip,
        }

    def save(self, path: str | Path) -> None:
        p = Path(path)
        p.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        logger.info("Config saved to %s", p.resolve())
