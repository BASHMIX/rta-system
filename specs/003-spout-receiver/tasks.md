# Tasks: Phase 1 — UI & Drawing Tools

**Input**: Design documents from `specs/003-spout-receiver/`

## Phase 8: ROI Backend

- [x] T034 Create `src/roi/__init__.py` with ROI base class and type registry
- [x] T035 Create `src/roi/base.py` — BaseROI: crop frame, apply mask, analyze
- [x] T036 Create `src/roi/health_bar.py` — HealthBarROI: multi-color sampling, fill %
- [x] T037 Create `src/roi/timer.py` — TimerROI: OCR for digits
- [x] T038 Create `src/roi/text_ocr.py` — TextROI: OCR for general text

## Phase 9: Drawing Canvas

- [x] T039 Create `src/ui/drawing_canvas.py` — screenshot load (JPG/PNG), mouse drag → rectangle, overlays, center guide line (X=960)
- [x] T040 Create `src/ui/widgets/roi_row.py` — single ROI row: name, type badge, coords, delete
- [x] T041 Create `src/ui/roi_list_panel.py` — scrollable ROI list with mirror button

## Phase 10: Panel Updates

- [x] T042 Rewrite `src/ui/tools_panel.py` — Upload Screenshot, tool type selector, SETUP/LIVE toggle, frame skip dropdown (0-10)
- [x] T043 Rewrite `src/ui/properties.py` — live X/Y/W/H, name input, OBS action (source + filter + action), Add ROI, Mirror to P2, Save Config
- [x] T044 Rewrite `src/ui/workspace.py` — replace video canvas with DrawingCanvas

## Phase 11: App Wiring

- [x] T045 Rewrite `src/ui/app.py` — wire all panels, LIVE mode skips canvas, frame skip logic
- [x] T046 Expand `src/spout/config.py` — ROI schema, save/load with UUID

## Phase 12: Performance

- [x] T047 Frame skip implementation (0-10 dropdown)
- [x] T048 LIVE mode: zero canvas rendering, grab-only loop
- [x] T049 Crop-first: sampler operates on `frame[y:y+h, x:x+w]` only
