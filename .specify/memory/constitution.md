<!--
  Sync Impact Report:
  - Version: 0.1.0 (initial)
  - All sections: created new
  - Templates requiring updates: none (initial)
  - Follow-up TODOs: RATIFICATION_DATE set to TODO — set on first ratified commit
-->

# Real-Time FGC Telemetry & OBS Automation System Constitution

## Core Principles

### I. Python Backend Engine
The entire analytical pipeline MUST be Python 3.10+ — Spout receiver → NumPy array → ROI crop/mask → segment math → delta calc → event dispatch. All detection logic lives in a worker thread detached from the UI. Rationale: CPU/GPU-bottleneck-free local processing.

### II. JSON-Driven Configuration
`config.json` is the single source of truth, loaded to RAM at startup with zero I/O during the monitoring loop. All ROI definitions, color ranges, segment parameters, and OBS event rules MUST be serialized here. No hardcoded per-game values in source code.

### III. Windows-Only, VRAM-to-VRAM Video Transport
Spout (DirectX shared texture) is the exclusive video input mechanism. Frame data MUST stay in GPU memory until the NumPy read. The system is Windows-only by design — no cross-platform abstraction layer.

### IV. Worker Thread Detached from UI
The CustomTkinter GUI is a configuration workspace only. At runtime the UI MAY be minimized. The analytical loop MUST run in a background `threading.Thread` that never blocks the UI event loop.

### V. OBS WebSocket Event Dispatch
All detected state changes dispatch via `obsws-python` (OBS WebSocket v5). Condition-action rules in `config.json` define the mapping from telemetry deltas (lifebar %, pixel density change, etc.) to scene item toggles and filter toggles.

## Technology Constraints

| Concern | Mandated Choice |
|---|---|
| Language | Python 3.10+ |
| Video transport | Spout-Python or SpoutGL (Windows, DirectX) |
| Computer vision | OpenCV (`cv2`), NumPy |
| GUI framework | CustomTkinter (dark-mode, native) |
| OBS control | `obsws-python` (WebSocket v5) |
| Config format | `config.json` |
| External AI/LLM | Prohibited at this stage (future layer) |
| Target platform | Windows only (Spout dependency) |

## Development Sprint Order

Execution MUST follow the roadmap sprint sequence — each sprint gates the next:

1. **Backend Core** — Establish Spout→Python→NumPy slice. Terminal logs from color thresholding.
2. **OBS Bridge** — `obsws-python` wrappers. Link terminal logs to actual OBS actions.
3. **Frontend** — CustomTkinter UI with Spout preview, drawing tools, JSON serialization.
4. **Math & Mirroring** — ROI segment math and P1→P2 mirror (`screen_width - x`, direction flip).
5. **System Polish** — Background threading finalised, CPU < 5% at idle.

## Governance

- The roadmap document (`Roadmap_Real-Time FGC Telemetry & OBS Automation System.md`) is the authoritative architecture reference.
- Where the roadmap contains duplicate sections, the **first occurrence** of each section is authoritative.
- Constitution amendments require documented rationale and must be reflected in the roadmap.
- The AGENTS.md file in the project root serves as runtime development guidance.
- Commit message format for constitution changes: `docs(constitution): <description>`.

**Version**: 0.1.0 | **Ratified**: TODO(RATIFICATION_DATE) | **Last Amended**: 2026-05-17
