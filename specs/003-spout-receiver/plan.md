# Implementation Plan: Spout Frame Receiver

**Branch**: `003-spout-receiver` | **Date**: 2026-05-17 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-spout-receiver/spec.md`

## Summary

Connect to a Spout sender (e.g., OBS Studio), capture video frames as NumPy arrays, sample pixel colors at configured coordinates, and print RGB/HSV values to the terminal at a configurable frame rate. This is Sprint 1 (Backend Core) from the roadmap — establishes the foundational Spout→NumPy pipeline.

## Technical Context

**Language/Version**: Python 3.10+

**Primary Dependencies**:
- Spout-Python (SpoutGL) — DirectX shared texture receiver (Windows-only)
- NumPy — frame array representation
- OpenCV (`cv2`) — color space conversion (BGR↔RGB↔HSV), optional frame utilities
- NEEDS CLARIFICATION: Which specific Spout Python package? SpoutGL (`pip install spoutgl`) is the maintained fork. Spout-Python is older. Need to verify which supports Python 3.10+ receiver mode.

**Storage**: N/A (terminal output, no persistence)

**Testing**: pytest with mock Spot sender or synthetic test pattern generator. NEEDS CLARIFICATION: How to test Spout receiver without a real GPU sender? Options: (a) synthetic NumPy frames injected before the Spout layer, (b) a headless Spout test sender, (c) pytest fixtures that bypass Spout entirely for unit tests.

**Target Platform**: Windows 10/11 (Spout requires DirectX 11)

**Project Type**: Console application / library module (entry point in `src/main.py`, receive logic in `src/spout/`)

**Performance Goals**: 30 FPS sustained capture-and-sample on mid-range gaming PC. Zero frame drops at target FPS. <2 second reconnection after sender restart.

**Constraints**: Must not exceed 5% CPU at idle (connected, static scene). Frame drops when system cannot keep up (no unbounded queuing). Spout sender name must match config exactly.

**Scale/Scope**: Single-sender, single-receiver. ~3 source files for this sprint.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Status | Rationale |
|------|--------|-----------|
| I. Python Backend Engine | **PASS** | Python 3.10+ NumPy frame processing in worker thread pattern |
| II. JSON-Driven Configuration | **PASS** | Sender name, sample points, target FPS from `config.json` |
| III. Windows-Only VRAM-to-VRAM | **PASS** | Spout (DirectX) is the video transport — Windows-only by design |
| IV. Worker Thread Detached from UI | **PASS** | Frame capture runs in background thread; no UI this sprint |
| V. OBS WebSocket Event Dispatch | **N/A** | No OBS event dispatch in this sprint |

**Result**: ALL GATES PASS — no violations. Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/003-spout-receiver/
├── plan.md              # This file
├── research.md          # Phase 0 — resolved unknowns
├── data-model.md        # Phase 1 — entities and validation
├── quickstart.md        # Phase 1 — setup and run guide
├── contracts/           # Phase 1 — interface contracts
│   ├── capture_pipeline.md
│   └── config_schema.md
└── tasks.md             # Created by /speckit.tasks
```

### Source Code (repository root)

```text
src/
├── spout/
│   ├── __init__.py
│   ├── receiver.py       # SpoutReceiver: connect, receive, disconnect
│   ├── sampler.py        # ColorSampler: sample pixel(s), RGB→HSV conversion
│   └── config.py         # SpoutConfig: load spout section from config.json
├── main.py               # Entry point — wire up receiver + sampler + loop
└── utils.py              # Color conversion helpers, clamping, logging helpers

tests/
├── __init__.py
├── test_receiver.py      # Unit tests with mock/Spout test pattern
├── test_sampler.py       # Unit tests for pixel sampling and conversion
└── test_config.py        # Config loading, validation, edge cases
```

**Structure Decision**: Single project structure with `src/spout/` package for all Sprint 1 code. This isolates the core backend module cleanly.

## Complexity Tracking

Not required — no Constitution violations.
