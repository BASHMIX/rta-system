from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

TOOL_TYPES = ["health_bar", "timer", "text"]


@dataclass
class ROI:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    tool_type: str = "health_bar"
    player: int = 1
    obs_source: str = ""
    obs_filter: str = ""
    obs_action: str = "visibility_on"
    mirrored_from: str = ""

    def crop(self, frame: np.ndarray) -> np.ndarray:
        h_img, w_img = frame.shape[:2]
        x1 = max(0, min(self.x, w_img - 1))
        y1 = max(0, min(self.y, h_img - 1))
        x2 = max(x1 + 1, min(self.x + self.width, w_img))
        y2 = max(y1 + 1, min(self.y + self.height, h_img))
        return frame[y1:y2, x1:x2]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "tool_type": self.tool_type,
            "player": self.player,
            "obs_source": self.obs_source,
            "obs_filter": self.obs_filter,
            "obs_action": self.obs_action,
            "mirrored_from": self.mirrored_from,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ROI":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", ""),
            x=data.get("x", 0),
            y=data.get("y", 0),
            width=data.get("width", 0),
            height=data.get("height", 0),
            tool_type=data.get("tool_type", "health_bar"),
            player=data.get("player", 1),
            obs_source=data.get("obs_source", ""),
            obs_filter=data.get("obs_filter", ""),
            obs_action=data.get("obs_action", "visibility_on"),
            mirrored_from=data.get("mirrored_from", ""),
        )

    def mirror(self, screen_width: int = 1920) -> "ROI":
        return ROI(
            id=str(uuid.uuid4())[:8],
            name=self.name.replace("P1", "P2").replace("p1", "p2"),
            x=screen_width - self.x - self.width,
            y=self.y,
            width=self.width,
            height=self.height,
            tool_type=self.tool_type,
            player=2,
            obs_source=self.obs_source,
            obs_filter=self.obs_filter,
            obs_action=self.obs_action,
            mirrored_from=self.name,
        )
