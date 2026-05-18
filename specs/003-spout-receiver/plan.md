# Implementation Plan: Phase 2 — UX Refinements & Canvas Polish

**Branch**: `003-spout-receiver` | **Date**: 2026-05-18 | **Spec**: [spec.md](./spec.md)

**Status**: 🔄 **IN PROGRESS** — Research & Data Model complete. Phase 13-16 implemented. Phase 17 (Integration & Polish) remaining.

## Summary

Refine Phase 1: ROI interaction (click/drag/resize), canvas scaling (native/1080p/720p), 16:9 canvas border + checkerboard, OBS hierarchy (Source → Filter).

## Research & Data Model
- [x] research.md generated
- [x] data-model.md generated


## Summary

Refine the Phase 1 implementation based on user feedback: ROI selection/move/resize, persistent tools, 16:9 canvas with signal scaling, live mode frame visibility fix, OBS source→filter hierarchy, and left panel tool list with delete.

## Technical Context

**Language/Version**: Python 3.10+ (conda env `rta_system`)

**Primary Dependencies**:
- CustomTkinter — dark-mode UI framework
- PIL (Pillow) — image loading, display, overlay rendering
- SpoutGL via SpoutLibrary.dll — frame capture (ctypes, GPU-affinity aware)
- obsws-python — OBS WebSocket v5 control (GetInputList, GetSourceFilterList)
- OpenCV (`cv2`) — HSV color conversion, image processing
- NumPy — array operations

**Storage**: `config.json` — single source of truth, explicit Save button, zero I/O during monitoring loop

**Target Platform**: Windows 10/11, NVIDIA GPU (isolated env routed via Windows Graphics Settings)

**Architecture Notes**:
- UI layer: configuration workspace only; minimized at runtime
- Worker thread: `CaptureThread` (background `threading.Thread`), UI updates via `after()` + `queue.Queue` bridge
- Canvas: 16:9 fixed aspect ratio, scale modes (native/1080p/720p)
- ROI interaction: click-to-select, drag-to-move, handle-drag-to-resize
- OBS hierarchy: source → filter (parent-child), actions applied to one target at a time

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Python Backend Engine | ✅ Compliant | Analytical loop runs in `CaptureThread` (background `threading.Thread`) |
| II. JSON-Driven Configuration | ✅ Compliant | `config.json` is single source of truth, explicit Save button |
| III. Windows-Only, VRAM-to-VRAM | ✅ Compliant | SpoutLibrary.dll + DirectX shared texture |
| IV. Worker Thread Detached from UI | ✅ Compliant | `CaptureThread` runs independently; UI updates via `after()` + `queue.Queue` bridge |
| V. OBS WebSocket Event Dispatch | ⏳ Future | OBS actions defined in config but dispatch logic not yet implemented |

## Project Structure

### Modified Files

```text
src/ui/
├── drawing_canvas.py        # Add: select/move/resize, 16:9 ratio, scale modes, live frame display
├── roi_list_panel.py        # Move to left panel, add (X) delete buttons
├── workspace.py             # Re-layout: left panel + center canvas + right properties
├── tools_panel.py           # Add: resolution scale selector (native/1080p/720p)
├── properties.py            # Add: OBS source dropdown + filter checkbox + filter dropdown
└── app.py                   # Wire: OBS source/filter list population, scale mode changes
src/obs/
└── client.py                # Add: get_source_filters(source_name) method
```

### Config Schema (Updated)

```json
{
  "spout": {
    "sender_name": "Spout_OBS_Filter",
    "target_fps": 30,
    "frame_skip": 2,
    "scale_mode": "1080p"
  },
  "rois": [
    {
      "id": "uuid-1",
      "name": "P1 HP",
      "x": 100, "y": 50, "width": 400, "height": 30,
      "tool_type": "health_bar",
      "player": 1,
      "obs_target": {
        "type": "source",
        "name": "Game Capture",
        "action": "visibility_on"
      }
    },
    {
      "id": "uuid-2",
      "name": "P1 Timer",
      "x": 500, "y": 50, "width": 100, "height": 30,
      "tool_type": "timer",
      "player": 1,
      "obs_target": {
        "type": "filter",
        "source": "Game Capture",
        "name": "Color Correction",
        "action": "filter_enable"
      }
    }
  ],
  "obs": {
    "host": "127.0.0.1",
    "port": 4455
  }
}
```

## Performance Rules

1. **LIVE mode skips canvas rendering** — `grab()` only, zero `set_canvas_image()` calls
2. **Crop-first** — all analysis on `frame[y:y+h, x:x+w]` only
3. **Frame skip** — configurable 0-10 via dropdown (0 = every frame, 10 = 1 of 11)
4. **Zero I/O during loop** — config loaded at startup, saved only on explicit button click
5. **ROI interaction < 50ms** — selection, move, resize must feel instantaneous

## Spec-to-Plan Mapping

| Spec Item | Plan Coverage | Status |
|-----------|---------------|--------|
| FR-001 to FR-016 | Phase 1 implementation | ✅ |
| FR-017: ROI click-to-select | `DrawingCanvas._on_press` hit-testing | 🔄 New |
| FR-018: ROI drag-to-move | `DrawingCanvas._on_drag` move logic | 🔄 New |
| FR-019: ROI resize handles | `DrawingCanvas` corner/edge handles | 🔄 New |
| FR-020: 16:9 aspect ratio | `DrawingCanvas` size enforcement | 🔄 New |
| FR-021: Signal scaling | Scale mode selector + canvas rescale | 🔄 New |
| FR-022: Live frame visibility | Fix overlay rendering (not masking) | 🔄 New |
| FR-023: OBS source list | `OBSClient.get_inputs()` → dropdown | 🔄 New |
| FR-024: OBS filter list | `OBSClient.get_source_filters()` → checkbox + dropdown | 🔄 New |
| FR-025: Left panel ROI list | `ROIListPanel` moved to left side | 🔄 New |
| FR-026: Panel→canvas selection sync | Click row → select ROI on canvas | 🔄 New |

## Open Issues

1. **HIGH**: FR-006 (disconnection retry) — no automatic reconnection logic.
2. **HIGH**: FR-009 (resolution change detection) — no buffer re-allocation on resolution change.
3. **MEDIUM**: FR-016 (OBS dispatch) — condition-action rules defined in config but dispatch engine not implemented.
