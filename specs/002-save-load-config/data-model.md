# Data Model: Save & Load Game Configs

## Entities

### GameProfile

A named snapshot of the full system configuration for one fighting game.

| Field | Type | Description | Constraints |
|---|---|---|---|
| `name` | `string` | User-defined profile name | 1–128 chars; unique across profiles |
| `system` | `SystemConfig` | Resolution, FPS, OBS WebSocket settings | Per roadmap config.json schema |
| `players` | `dict[str, PlayerConfig]` | P1 and P2 configurations | Keys: "P1", "P2" |
| `obs_events` | `list[OBSEvent]` | Condition-action rules | Per roadmap config.json schema |
| `created_at` | `string` (ISO 8601) | Profile creation timestamp | Auto-set on creation |
| `updated_at` | `string` (ISO 8601) | Last modification timestamp | Auto-updated on save |

**Relationships**:
- A `GameProfile` is the full config — it owns all ROIs, rules, and settings.
- No relationship between profiles (fully independent).

**Validation rules**:
- `name` must be non-empty and unique (case-insensitive comparison).
- `system` must contain valid resolution (width, height > 0) and target_fps (≥ 1).
- `obs_websocket` within system must have host, port, and password.
- Each player's ROIs must have valid coordinates (within screen bounds).
- `obs_events` must have non-empty trigger names and at least one action.

### ProfileIndex

A lightweight catalog of all profiles for fast list rendering.

| Field | Type | Description |
|---|---|---|
| `profiles` | `list[ProfileEntry]` | Ordered list of profile summaries |
| `last_loaded` | `string` \| `null` | Name of the last-loaded profile |

### ProfileEntry

A summary entry in the profile index.

| Field | Type | Description |
|---|---|---|
| `name` | `string` | Profile name |
| `created_at` | `string` (ISO 8601) | Creation timestamp |
| `updated_at` | `string` (ISO 8601) | Last modified timestamp |
| `game_summary` | `string` | Human-readable summary (e.g., "4 ROIs, 2 events") |

## State Transitions

```
[Fresh Start]
    |
    v
[No Profiles] -- Save As --> [Profile List + 1 entry]
    |                            |
    |                            v
    |                       [Profile Selected] -- Load --> [Config Applied]
    |                            |                            |
    |                            +-- Rename --> [Name Updated] |
    |                            |                            |
    |                            +-- Delete --> [Entry Removed]
    |                            |                            |
    |                            +-- Duplicate --> [Copy Created]
    |                            |                            |
    |                            +-- Export --> [File Exported]
    |                            |
    +-- Import --> [Profile Added]
    |
    v
[Last Profile Restored on App Start]
```

## Profile Directory Layout

```text
profiles/
├── index.json              # ProfileIndex: order, last-loaded tracking
├── street-fighter-6.json   # GameProfile (sanitized name)
├── tekken-8.json
└── guilty-gear-strive.json
```
