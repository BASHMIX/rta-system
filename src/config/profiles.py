import json
import shutil
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.config.models import GameProfile, ProfileEntry, ProfileIndex, OBSWebSocketConfig
from src.config.schema import sanitize_profile_name, validate_game_profile


class ProfileManager:
    def __init__(self, profiles_dir: str | Path = "profiles"):
        self._lock = threading.Lock()
        self._profiles_dir = Path(profiles_dir)
        self._profiles_dir.mkdir(parents=True, exist_ok=True)
        self._index = self._load_index()

    @property
    def profiles_dir(self) -> Path:
        return self._profiles_dir

    @property
    def profile_names(self) -> list[str]:
        return [p.name for p in self._index.profiles]

    @property
    def last_loaded_name(self) -> Optional[str]:
        return self._index.last_loaded

    def _index_path(self) -> Path:
        return self._profiles_dir / "index.json"

    def _profile_path(self, name: str) -> Path:
        return self._profiles_dir / f"{sanitize_profile_name(name)}.json"

    def _load_index(self) -> ProfileIndex:
        index_path = self._index_path()
        if not index_path.exists():
            return ProfileIndex()
        try:
            with open(index_path, "r") as f:
                data = json.load(f)
            profiles = [
                ProfileEntry(**entry) for entry in data.get("profiles", [])
            ]
            return ProfileIndex(
                profiles=profiles,
                last_loaded=data.get("last_loaded"),
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            return ProfileIndex()

    def _save_index(self) -> None:
        index_data = {
            "profiles": [
                {
                    "name": p.name,
                    "created_at": p.created_at,
                    "updated_at": p.updated_at,
                    "game_summary": p.game_summary,
                }
                for p in self._index.profiles
            ],
            "last_loaded": self._index.last_loaded,
        }
        with open(self._index_path(), "w") as f:
            json.dump(index_data, f, indent=2)

    def save(self, name: str, config: GameProfile) -> GameProfile:
        with self._lock:
            name_err = [e for e in validate_game_profile(config.to_dict()) if "name" in e]
            profile = GameProfile(
                name=name,
                system=config.system,
                players=config.players,
                obs_events=config.obs_events,
                created_at=config.created_at or datetime.now(timezone.utc).isoformat(),
                updated_at=datetime.now(timezone.utc).isoformat(),
            )
            profile_dict = profile.to_dict()
            profile_path = self._profile_path(name)
            with open(profile_path, "w") as f:
                json.dump(profile_dict, f, indent=2)
            existing = [p for p in self._index.profiles if p.name == name]
            if existing:
                existing[0].updated_at = profile.updated_at
            else:
                entry = ProfileEntry(
                    name=name,
                    created_at=profile.created_at,
                    updated_at=profile.updated_at,
                    game_summary=self._compute_summary(profile),
                )
                self._index.profiles.append(entry)
            self._index.last_loaded = name
            self._save_index()
            return profile

    def load(self, name: str) -> GameProfile:
        with self._lock:
            profile_path = self._profile_path(name)
            if not profile_path.exists():
                raise FileNotFoundError(f"Profile '{name}' not found")
            try:
                with open(profile_path, "r") as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Profile '{name}' is corrupted: {e}")
            errors = validate_game_profile(data)
            if errors:
                raise ValueError(f"Profile '{name}' validation failed: {'; '.join(errors)}")
            self._index.last_loaded = name
            self._save_index()
            return GameProfile.from_dict(data)

    def confirm_overwrite(self, name: str) -> bool:
        with self._lock:
            return any(p.name == name for p in self._index.profiles)

    def rename(self, old_name: str, new_name: str) -> None:
        with self._lock:
            if not any(p.name == old_name for p in self._index.profiles):
                raise FileNotFoundError(f"Profile '{old_name}' not found")
            if any(p.name == new_name for p in self._index.profiles):
                raise FileExistsError(f"Profile '{new_name}' already exists")
            old_path = self._profile_path(old_name)
            new_path = self._profile_path(new_name)
            if old_path.exists():
                old_path.rename(new_path)
            for entry in self._index.profiles:
                if entry.name == old_name:
                    entry.name = new_name
                    entry.updated_at = datetime.now(timezone.utc).isoformat()
                    break
            if self._index.last_loaded == old_name:
                self._index.last_loaded = new_name
            self._save_index()

    def delete(self, name: str) -> None:
        with self._lock:
            profile_path = self._profile_path(name)
            if profile_path.exists():
                profile_path.unlink()
            self._index.profiles = [p for p in self._index.profiles if p.name != name]
            if self._index.last_loaded == name:
                self._index.last_loaded = self._index.profiles[0].name if self._index.profiles else None
            self._save_index()

    def duplicate(self, name: str, suffix: str = "Copy") -> str:
        with self._lock:
            if not any(p.name == name for p in self._index.profiles):
                raise FileNotFoundError(f"Profile '{name}' not found")
            new_name = f"{name} ({suffix})"
            if any(p.name == new_name for p in self._index.profiles):
                counter = 1
                while any(p.name == f"{new_name} {counter}" for p in self._index.profiles):
                    counter += 1
                new_name = f"{new_name} {counter}"
            profile = self.load(name)
            profile.name = new_name
            profile.created_at = datetime.now(timezone.utc).isoformat()
            profile.updated_at = datetime.now(timezone.utc).isoformat()
            self.save(new_name, profile)
            return new_name

    def export(self, name: str, target_path: str | Path) -> None:
        with self._lock:
            profile = self.load(name)
            target = Path(target_path)
            with open(target, "w") as f:
                json.dump(profile.to_dict(), f, indent=2)

    def import_(self, source_path: str | Path) -> str:
        source = Path(source_path)
        with open(source, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Import file is not valid JSON: {e}")
        errors = validate_game_profile(data)
        if errors:
            raise ValueError(f"Import file validation failed: {'; '.join(errors)}")
        with self._lock:
            name = data["name"]
            if any(p.name == name for p in self._index.profiles):
                counter = 1
                while any(p.name == f"{name} (imported {counter})" for p in self._index.profiles):
                    counter += 1
                name = f"{name} (imported {counter})"
            profile = GameProfile.from_dict(data)
            profile.name = name
            profile.created_at = datetime.now(timezone.utc).isoformat()
            profile.updated_at = datetime.now(timezone.utc).isoformat()
            self.save(name, profile)
            return name

    def get_profile_summary(self, name: str) -> dict:
        with self._lock:
            for entry in self._index.profiles:
                if entry.name == name:
                    return {
                        "name": entry.name,
                        "created_at": entry.created_at,
                        "updated_at": entry.updated_at,
                        "roi_count": self._count_rois(name),
                    }
            raise FileNotFoundError(f"Profile '{name}' not found")

    def _compute_summary(self, profile: GameProfile) -> str:
        roi_count = sum(
            1 for p in profile.players.values()
            for roi in [p.lifebar, p.combo_counter, p.system_text_zone]
            if roi is not None
        )
        event_count = len(profile.obs_events)
        return f"{roi_count} ROIs, {event_count} events"

    def _count_rois(self, name: str) -> int:
        try:
            profile = self.load(name)
            return sum(
                1 for p in profile.players.values()
                for roi in [p.lifebar, p.combo_counter, p.system_text_zone]
                if roi is not None
            )
        except (FileNotFoundError, ValueError):
            return 0

    def check_obs_credential_diff(self, profile_name: str, current_ws: OBSWebSocketConfig) -> Optional[dict]:
        try:
            profile = self.load(profile_name)
            target = profile.system.obs_websocket
            diffs = {}
            if target.host != current_ws.host:
                diffs["host"] = (current_ws.host, target.host)
            if target.port != current_ws.port:
                diffs["port"] = (current_ws.port, target.port)
            if target.password != current_ws.password:
                diffs["password"] = ("****", "****")
            return diffs if diffs else None
        except (FileNotFoundError, ValueError):
            return None
