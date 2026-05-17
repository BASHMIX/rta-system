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

**Storage**: `config.json` — single source of truth, explicit Save button

**Target Platform**: Windows 10/11, NVIDIA GPU (isolated env routed via Windows Graphics Settings)

## Project Structure

### New Source Files

```text
src/
├── roi/
│   ├── __init__.py
│   ├── base.py              # Base ROI: crop, mask, analyze
│   ├── health_bar.py        # Multi-color sampling across bar area
│   ├── timer.py             # OCR for timer digits
│   └── text_ocr.py          # OCR for general text
├── ui/
│   ├── drawing_canvas.py    # Screenshot display, rectangle overlays, center guide (X=960)
│   ├── roi_list_panel.py    # Scrollable ROI list
│   └── widgets/
│       └── roi_row.py       # Single ROI row widget
```

### Modified Files

```text
src/ui/
├── tools_panel.py           # Upload Screenshot (JPG/PNG), tool selector, SETUP/LIVE toggle, frame skip dropdown
├── workspace.py             # Replace video canvas with DrawingCanvas
├── properties.py            # Live X/Y/W/H, name input, OBS action assignment, Add ROI, Mirror, Save Config
├── app.py                   # Wire panels, LIVE mode skips canvas, frame skip logic
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
      "obs_action": "visibility_on"
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
| **Health Bar** | Samples center row left→right, finds health→background transition | Fill percentage (0-100) |
| **Timer** | OCR on digit area | Numeric value |
| **Text** | OCR on text area | String value |

All three are scalable rectangles. The difference is only in post-crop analysis.

## Performance Rules

1. **LIVE mode skips canvas rendering** — `grab()` only, zero `set_canvas_image()` calls
2. **Crop-first** — all analysis on `frame[y:y+h, x:x+w]` only
3. **Frame skip** — configurable 0-10 via dropdown (0 = every frame, 10 = 1 of 11)
