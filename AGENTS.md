# AGENTS.md — Real-Time FGC Telemetry & OBS Automation System

## Status

This repository is **pre-implementation** (greenfield). The only source of truth is the project roadmap:
- `Roadmap_Real-Time FGC Telemetry & OBS Automation System.md` — architecture, tech stack, JSON schema, dev sprints.

There is no code, build system, CI, tests, or package manager config yet. All work will create the project from scratch.

## Predetermined Tech Stack (from roadmap)

| Concern | Choice |
|---|---|
| Language | Python 3.10+ |
| Video transport | Spout-Python or SpoutGL (VRAM-to-VRAM, Windows) |
| CV | OpenCV (`cv2`), NumPy |
| GUI | CustomTkinter (dark-mode, native Windows) |
| OBS control | `obsws-python` (OBS WebSocket v5) |
| Config format | `config.json` — single source of truth loaded to RAM at startup |

## Architecture (planned)

- **UI layer**: configuration workspace only; minimized at runtime
- **Worker thread**: detached from UI, runs the analytical loop (Spout → NumPy → ROI crop/mask → segment math → delta calc → event dispatch)
- **OBS Events**: condition-action rules in `config.json` (toggle source/filter via WebSocket)
- **P1→P2 Mirror**: coordinate inversion (`screen_width - x`) + direction flip

## Development Order (Sprints from roadmap)

1. Backend Core: Spout→Python→NumPy slice→terminal logs from color thresholding
2. OBS Bridge: `obsws-python` wrappers, link logs to OBS actions
3. Frontend: CustomTkinter UI, Spout preview, drawing tools, JSON serialization
4. Math & Mirroring: ROI segmentation, P1→P2 mirror calculations
5. System Polish: background threading, CPU < 5% idle

## Key Gotchas

- Spout is **Windows-only** (DirectX shared texture). Development is Windows-only.
- The roadmap document contains repeated/duplicate sections. The **first occurrence** of each section is authoritative.
- No external AI/LLM dependencies at this stage (roadmap positions AI as a "future" layer).
