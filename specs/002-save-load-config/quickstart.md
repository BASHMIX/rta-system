# Quickstart: Save & Load Game Configs

## What This Feature Does

Allows RTA users to save their full configuration (ROIs, event rules, system
settings) as a named **game profile** and load it later. This means:

- Configure ROIs for **Street Fighter 6** once, save as "Street Fighter 6"
- Switch to **Tekken 8** — load the Tekken profile, all settings swap
- No need to re-draw ROIs or re-enter OBS credentials when switching games

## Key Capabilities

| Operation | What Happens |
|---|---|
| **Save As** | Current config saved as a named profile |
| **Load** | Selected profile replaces current config |
| **Rename** | Profile name updated in the list |
| **Delete** | Profile permanently removed |
| **Duplicate** | Exact copy made (good for A/B testing settings) |
| **Export** | Profile saved as standalone `.json` file for sharing/backup |
| **Import** | Profile loaded from external `.json` file |

## First-Time Flow

1. Launch RTA, configure ROIs and rules for your game
2. Click **Save Current As...**
3. Type a name (e.g., "Street Fighter 6"), click **Save**
4. The profile appears in the saved profiles list
5. Next session: profile auto-loads

## Switching Games

1. Click a different profile in the saved list
2. Click **Load**
3. If the profile has different OBS credentials, you'll be prompted to
   reconnect
4. All ROIs and rules swap to the loaded profile — start monitoring immediately

## File Locations

| Path | Contents |
|---|---|
| `profiles/` | All saved profiles (back this up!) |
| `profiles/<name>.json` | Individual profile file |
| `profiles/index.json` | Profile list and last-loaded tracking |

## Notes

- Profiles are plain JSON — you can inspect or edit them in any text editor
- Export creates a standalone file you can share with other RTA users
- The `profiles/` directory is excluded from git (user data, not code)
