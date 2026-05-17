from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


@dataclass
class OBSAction:
    type: str
    scene: Optional[str] = None
    source: Optional[str] = None
    filter: Optional[str] = None
    state: Optional[bool] = None


@dataclass
class OBSEvent:
    trigger: str
    condition: str
    actions: list[OBSAction] = field(default_factory=list)


@dataclass
class ROIConfig:
    roi: list[int]
    direction: str
    segments: int
    target_color_hsv_range: list[list[int]]


@dataclass
class PlayerConfig:
    lifebar: Optional[ROIConfig] = None
    combo_counter: Optional[ROIConfig] = None
    system_text_zone: Optional[ROIConfig] = None


@dataclass
class OBSWebSocketConfig:
    host: str = "localhost"
    port: int = 4455
    password: str = ""


@dataclass
class SystemConfig:
    resolution: list[int] = field(default_factory=lambda: [1920, 1080])
    target_fps: int = 30
    obs_websocket: OBSWebSocketConfig = field(default_factory=OBSWebSocketConfig)


@dataclass
class GameProfile:
    name: str
    system: SystemConfig = field(default_factory=SystemConfig)
    players: dict[str, PlayerConfig] = field(default_factory=dict)
    obs_events: list[OBSEvent] = field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        now = datetime.now(timezone.utc).isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "GameProfile":
        return cls(
            name=data["name"],
            system=SystemConfig(**data.get("system", {})),
            players={
                k: PlayerConfig(
                    lifebar=ROIConfig(**v["lifebar"]) if v.get("lifebar") else None,
                    combo_counter=ROIConfig(**v["combo_counter"]) if v.get("combo_counter") else None,
                    system_text_zone=ROIConfig(**v["system_text_zone"]) if v.get("system_text_zone") else None,
                )
                for k, v in data.get("players", {}).items()
            },
            obs_events=[
                OBSEvent(
                    trigger=e["trigger"],
                    condition=e["condition"],
                    actions=[OBSAction(**a) for a in e.get("actions", [])],
                )
                for e in data.get("obs_events", [])
            ],
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


@dataclass
class ProfileEntry:
    name: str
    created_at: str
    updated_at: str
    game_summary: str = ""


@dataclass
class ProfileIndex:
    profiles: list[ProfileEntry] = field(default_factory=list)
    last_loaded: Optional[str] = None
