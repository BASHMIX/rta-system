# Implementation Plan: Phase 1 — UI & Drawing Tools

**Branch**: `003-spout-receiver` | **Date**: 2026-05-17 | **Spec**: [spec.md](./spec.md)

**Status**: ✅ **COMPLETE** — All tasks T034-T049 implemented and verified.

## Summary

Build the interactive configuration workspace: upload a static HUD screenshot, draw scalable ROI rectangles (Health Bar, Timer, Text), assign custom names and OBS actions, mirror coordinates for P2, and export to `config.json`. LIVE mode disables canvas rendering for zero-overhead capture.

## Technical Context

**Language/Version**: Python 3.10+ (conda env `rta_system`)

**Primary Dependencies**:
- CustomTkinter — dark-mode UI framework
- PIL (Pillow) — image loading, display
- SpoutGL via SpoutLibrary.dll — frame capture (ctypes, GPU-affinity aware)
- obsws-python — OBS WebSocket v5 control
- OpenCV (`cv2`) — HSV color conversion, image processing
- NumPy — array operations

**Storage**: `config.json` — single source of truth, explicit Save button, zero I/O during monitoring loop

**Target Platform**: Windows 10/11, NVIDIA GPU (isolated env routed via Windows Graphics Settings)

**Architecture Notes**:
- UI layer: configuration workspace only; minimized at runtime
- Worker thread: detached from UI, runs the analytical loop (Spout → NumPy → ROI crop/mask → segment math → delta calc → event dispatch)
- OBS Events: condition-action rules in `config.json` (toggle source/filter via WebSocket)
- P1→P2 Mirror: coordinate inversion (`screen_width - x`) + direction flip

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Python Backend Engine | ✅ Compliant | Analytical loop runs in `CaptureThread` (background `threading.Thread`) |
| II. JSON-Driven Configuration | ✅ Compliant | `config.json` is single source of truth, explicit Save button |
| III. Windows-Only, VRAM-to-VRAM | ✅ Compliant | SpoutLibrary.dll + DirectX shared texture |
| IV. Worker Thread Detached from UI | ✅ Compliant | `CaptureThread` runs independently; UI updates via `after()` + `queue.Queue` bridge |
| V. OBS WebSocket Event Dispatch | ⏳ Future | OBS actions defined in config but dispatch logic not yet implemented |

## Project Structure

### New Source Files

```text
src/
├── roi/
│   ├── __init__.py          # ROI dataclass, crop, mirror, serialize
│   ├── base.py              # BaseAnalyzer: abstract analyze()
│   ├── health_bar.py        # HSV center-row sampling → fill %
│   ├── timer.py             # OCR for timer digits (pytesseract)
│   └── text_ocr.py          # OCR for general text (pytesseract)
├── ui/
│   ├── drawing_canvas.py    # Screenshot display, drag-to-draw, center guide (X=960)
│   ├── roi_list_panel.py    # Scrollable ROI list
│   └── widgets/
│       └── roi_row.py       # Single ROI row widget
```

### Modified Files

```text
src/ui/
├── tools_panel.py           # Upload Screenshot (JPG/PNG), tool selector, SETUP/LIVE toggle, frame skip dropdown
├── workspace.py             # Replace video canvas with DrawingCanvas + ROI list sidebar
├── properties.py            # Live X/Y/W/H, name input, OBS action assignment, Add ROI, Mirror, Save Config
├── app.py                   # Wire panels, LIVE mode skips canvas, frame skip logic
src/spout/
└── config.py                # Expanded schema: rois array, obs section, frame_skip
```

### Config Schema

```json
{
  "spout": {
    "sender_name": "Spout_OBS_Filter",
    "target_fps": 30,
    "frame_skip": 2
  },
  "rois": [
    {
      "id": "uuid-1",
      "name": "P1 HP",
      "x": 100, "y": 50, "width": 400, "height": 30,
      "tool_type": "health_bar",
      "player": 1,
      "obs_source": "Game Capture",
      "obs_filter": "",
      "obs_action": "visibility_on",
      "mirrored_from": ""
    }
  ],
  "obs": {
    "host": "127.0.0.1",
    "port": 4455
  }
}
```

## Tool Types

| Type | Analysis | Output |
|------|----------|--------|
| **Health Bar** | Samples center row left→right, finds health→background transition via HSV | Fill percentage (0-100) |
| **Timer** | OCR on digit area (pytesseract, optional) | Numeric string |
| **Text** | OCR on text area (pytesseract, optional) | String value |

All three are scalable rectangles. The difference is only in post-crop analysis.

## Performance Rules

1. **LIVE mode skips canvas rendering** — `grab()` only, zero `set_canvas_image()` calls
2. **Crop-first** — all analysis on `frame[y:y+h, x:x+w]` only
3. **Frame skip** — configurable 0-10 via dropdown (0 = every frame, 10 = 1 of 11)
4. **Zero I/O during loop** — config loaded at startup, saved only on explicit button click

## Spec-to-Plan Mapping

| Spec Item | Plan Coverage | Status |
|-----------|---------------|--------|
| FR-001: Spout connection | `SpoutGLSource.open()`, `grab()` | ✅ |
| FR-002: NumPy RGBA frames | `_GLContext` + `receiveTexture` + `glGetTexImage` | ✅ |
| FR-003: Sample at coords | `ROI.crop()` + analyzer pipeline | ✅ |
| FR-004: Print RGB/HSV | `health_bar.py` → `logger.info()` | ✅ |
| FR-005: Configurable FPS | `frame_skip` dropdown 0-10 | ✅ |
| FR-006: Disconnection handling | `grab()` returns `None` on failure | ⚠️ Needs retry logic |
| FR-007: Config file | `config.json` load/save | ✅ |
| FR-008: OOB clamping | `ROI.crop()` clamps to frame bounds | ✅ |
| FR-009: Resolution change | Not yet implemented | ❌ Gap |
| FR-010: Drawing canvas | `DrawingCanvas` class | ✅ |
| FR-011: Tool types | `health_bar.py`, `timer.py`, `text_ocr.py` | ✅ |
| FR-012: ROI serialization | `ROI.to_dict()`, `from_dict()` | ✅ |
| FR-013: P2 mirroring | `ROI.mirror(screen_width=1920)` | ✅ |
| FR-014: SETUP/LIVE mode | `_mode` flag, canvas skip | ✅ |
| FR-015: Frame skip | `_frame_skip`, `_skip_counter` | ✅ |
| FR-016: OBS dispatch | Not yet implemented | ❌ Gap (future sprint) |

## Open Issues

1. **HIGH**: FR-006 (disconnection retry) — no automatic reconnection logic.
2. **HIGH**: FR-009 (resolution change detection) — no buffer re-allocation on resolution change.
3. **MEDIUM**: FR-016 (OBS dispatch) — condition-action rules defined in config but dispatch engine not implemented.
