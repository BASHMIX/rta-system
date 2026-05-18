# Tasks: Phase 2 — UX Refinements & Canvas Polish

**Input**: Design documents from `specs/003-spout-receiver/`

## Phase 13: ROI Selection & Interaction

- [x] T051 Add hit-testing to `DrawingCanvas._on_press` — detect click inside existing ROI vs empty canvas
- [x] T052 Implement ROI selection state — highlight border, show resize handles, update properties panel
- [x] T053 Implement drag-to-move — track offset, update ROI x/y in real-time, sync to properties panel
- [x] T054 Implement resize handles — 8 handles (4 corners + 4 edges), drag to resize, update width/height in real-time
- [x] T055 Add click-outside-to-deselect — clicking empty canvas starts new drawing, deselects current ROI
- [x] T056 Fix live mode frame visibility — overlays render on top of video feed (semi-transparent), not as masks

## Phase 14: Canvas 16:9 & Scaling

- [x] T057 Enforce 16:9 aspect ratio on `DrawingCanvas` — calculate from parent container, maintain on resize
- [x] T058 Add scale mode selector to `ToolsPanel` — dropdown: Native, 1080p, 720p
- [x] T059 Implement scale mode switching — rescale video feed and ROI overlays proportionally
- [x] T060 Update coordinate mapping — canvas-to-screen and screen-to-canvas conversions respect scale mode

## Phase 15: Left Panel ROI List

- [x] T061 Move `ROIListPanel` from right sidebar to left panel in `workspace.py` layout
- [x] T062 Add (X) delete button to each `ROIRow` — remove ROI from list, canvas, and config
- [x] T063 Add click-to-select sync — clicking row selects ROI on canvas, highlights it
- [x] T064 Update `workspace.py` layout: left panel (ROI list) → center (canvas) → right (properties)

## Phase 16: OBS Source/Filter Hierarchy

- [x] T065 Add `get_source_filters(source_name)` method to `OBSClient` — returns list of filter names
- [x] T066 Rewrite `properties.py` OBS section — source dropdown → optional filter checkbox → filter dropdown
- [x] T067 Populate source dropdown from `OBSClient.get_inputs()` on connect
- [x] T068 Populate filter dropdown when checkbox enabled — call `get_source_filters(selected_source)`
- [x] T069 Update `OBSTarget` data model — replace flat `obs_source`/`obs_filter`/`obs_action` with hierarchical structure
- [x] T070 Update `ROI.to_dict()` / `from_dict()` — serialize/deserialize new `obs_target` structure

## Phase 17: Integration & Polish

- [ ] T071 Wire scale mode changes to `CaptureThread` — update frame scaling in background thread
- [ ] T072 Add minimum ROI size constraint (10x10 pixels) — enforce in resize and save
- [ ] T073 Add ROI coordinate clamping on save — ensure all ROIs within screen bounds
- [ ] T074 Update `config.json` schema — add `scale_mode` field, migrate `obs_target` structure
- [ ] T075 Test end-to-end: draw → select → move → resize → assign OBS action → save → reload
