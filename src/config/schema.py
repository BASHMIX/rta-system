import re


def sanitize_profile_name(name: str) -> str:
    sanitized = name.lower()
    sanitized = re.sub(r"[^a-z0-9\-_\.]", "-", sanitized)
    sanitized = re.sub(r"-{2,}", "-", sanitized)
    sanitized = sanitized.strip("-")
    return sanitized if sanitized else "unnamed"


def validate_profile_name(name: str) -> str | None:
    if not name or not name.strip():
        return "Profile name must not be empty"
    if len(name) > 128:
        return "Profile name must be 128 characters or fewer"
    return None


def validate_resolution(resolution: list[int]) -> str | None:
    if len(resolution) != 2:
        return "Resolution must be [width, height]"
    if resolution[0] <= 0 or resolution[1] <= 0:
        return "Resolution dimensions must be positive"
    return None


def validate_obs_websocket(host: str, port: int) -> str | None:
    if not host:
        return "OBS WebSocket host must not be empty"
    if not (1 <= port <= 65535):
        return "OBS WebSocket port must be between 1 and 65535"
    return None


def validate_game_profile(data: dict) -> list[str]:
    errors: list[str] = []
    if "name" not in data:
        errors.append("Profile must have a 'name' field")
    else:
        name_err = validate_profile_name(data["name"])
        if name_err:
            errors.append(name_err)
    system = data.get("system", {})
    res_err = validate_resolution(system.get("resolution", [1920, 1080]))
    if res_err:
        errors.append(f"system.resolution: {res_err}")
    ws = system.get("obs_websocket", {})
    ws_err = validate_obs_websocket(ws.get("host", "localhost"), ws.get("port", 4455))
    if ws_err:
        errors.append(f"system.obs_websocket: {ws_err}")
    players = data.get("players", {})
    for player_key in players:
        for roi_key in ["lifebar", "combo_counter", "system_text_zone"]:
            roi = players[player_key].get(roi_key)
            if roi:
                if len(roi.get("roi", [])) != 4:
                    errors.append(f"{player_key}.{roi_key}.roi must have exactly 4 values")
    obs_events = data.get("obs_events", [])
    for i, event in enumerate(obs_events):
        if not event.get("trigger"):
            errors.append(f"obs_events[{i}].trigger must not be empty")
        if not event.get("actions"):
            errors.append(f"obs_events[{i}] must have at least one action")
    return errors
