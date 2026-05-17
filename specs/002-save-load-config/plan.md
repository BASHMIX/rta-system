# Implementation Plan: Save & Load Game Configs

**Branch**: `main` | **Date**: 2026-05-17 | **Spec**: `specs/002-save-load-config/spec.md`

**Input**: Feature specification from `specs/002-save-load-config/spec.md`

## Summary

Add per-game profile save/load to the RTA system. Each profile is a named JSON
snapshot of the full configuration (ROIs, player settings, event rules, system
settings). Profiles stored as individual files in a `profiles/` directory.
Users can save, load, rename, delete, duplicate, export, and import profiles
via the CustomTkinter UI.

## Technical Context

**Language/Version**: Python 3.10+

**Primary Dependencies**: CustomTkinter (UI), `obsws-python` (OBS WebSocket),
stdlib `json`, `pathlib`, `shutil` (file management)

**Storage**: File-based — individual JSON files in `profiles/` directory at
project root. Profile JSON extends the `config.json` schema from the roadmap.

**Testing**: `pytest` with `unittest.mock` for file I/O and OBS WebSocket.
Test profiles in a temp directory fixture.

**Target Platform**: Windows (Spout dependency)

**Project Type**: Desktop GUI app with background worker thread

**Performance Goals**: Profile save/load completes in under 1 second for a
typical config (~50 KB). Profile list refresh in under 100ms for 50 profiles.

**Constraints**: File I/O must never block the UI thread. Profile corruption
must not crash the app. All profile operations must be safe against concurrent
write from the monitoring worker.

**Scale/Scope**: 50 concurrent profiles supported. Single-user local machine
(no network or multi-user concerns in scope).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Constitution Rule | Assessment | Justification |
|---|---|---|
| **II. JSON-Driven Configuration** | ✅ PASS — Profiles are JSON files extending the `config.json` pattern. Single source of truth per profile. | |
| **IV. Worker Thread Detached from UI** | ✅ PASS — Save/load is UI-triggered but file I/O runs on background thread. Profile switching does not block the event loop. | |
| **V. OBS WebSocket Event Dispatch** | ⚠️ CONDITIONAL — Profile switching that changes OBS WebSocket credentials must prompt reconnection. If no credential change, no reconnection needed. | Implement a credential-diff check on profile load. |
| **Sprint Order** | ✅ PASS — This feature belongs to Sprint 3 (Frontend) with minor dependencies on Sprint 2 (OBS Bridge for reconnection handler). No Sprint 1 (Backend Core) prerequisites needed. | |

## Project Structure

### Documentation (this feature)

```text
specs/002-save-load-config/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── main.py
├── config/
│   ├── __init__.py
│   ├── models.py
│   ├── profiles.py      # Profile CRUD: save, load, list, rename, delete, duplicate, export, import
│   └── schema.py
├── capture/
│   ├── __init__.py
│   ├── spout_receiver.py
│   └── frame_processor.py
├── analysis/
│   ├── __init__.py
│   ├── roi.py
│   ├── health_bar.py
│   └── text_detector.py
├── obs/
│   ├── __init__.py
│   ├── bridge.py
│   └── events.py
├── ui/
│   ├── __init__.py
│   ├── app.py
│   ├── canvas.py
│   ├── toolbar.py
│   ├── profile_manager.py  # Profile list widget, Save As dialog, Import/Export dialogs
│   └── widgets/
└── worker/
    ├── __init__.py
    └── monitor_thread.py

tests/
├── test_profiles.py
├── test_config.py
└── conftest.py
```

**Structure Decision**: Single-source Python package with `src/` layout.
Feature-specific code in `src/config/profiles.py` (core logic) and
`src/ui/profile_manager.py` (UI). Standard `tests/` mirror.

## Complexity Tracking

No Constitution Check violations — feature is within all architecture constraints.
