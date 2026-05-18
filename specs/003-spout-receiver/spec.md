# Feature Specification: Spout Frame Receiver

**Feature Branch**: `003-spout-receiver`

**Created**: 2026-05-17

**Status**: Draft

**Input**: User description: "Spout receiver that captures frames and prints color values to terminal"

**Clarification 2026-05-17**: Scope expanded from terminal-only (Sprint 1) to include Phase 1 UI & Drawing Tools (Sprint 3 frontend): interactive screenshot workspace, ROI rectangle drawing, custom naming, OBS action assignment, P2 mirroring, and `config.json` export.

**Refinement 2026-05-17**: UX improvements — ROI selection/editing, persistent tools, 16:9 canvas with scaling, OBS source→filter hierarchy, live mode frame visibility fix.

## Clarifications

### Session 2026-05-17

- Q: Should the spec be updated to include Phase 1 UI scope or kept as Sprint 1 only? → A: Update existing spec to include UI + ROI tool scope, keeping all sprint artifacts in one feature branch for traceability.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Capture Frames from a Spout Sender (Priority: P1)

A streamer has OBS running with a Spout output plugin. They launch the RTA system which connects to the Spout sender and begins receiving live game frames in real-time.

**Why this priority**: Without frame capture, no downstream analysis is possible. This is the foundational data pipeline.

**Independent Test**: Can be fully tested by running a Spout sender (test pattern), launching the receiver, and verifying frames arrive at the expected resolution and framerate.

**Acceptance Scenarios**:

1. **Given** a Spout sender is broadcasting, **When** the receiver connects by sender name, **Then** frames of matching resolution begin arriving
2. **Given** frames are arriving, **When** inspected, **Then** each frame matches the sender's resolution and pixel format
3. **Given** the sender stops broadcasting, **When** the connection drops, **Then** the receiver logs the disconnection without crashing

---

### User Story 2 - Print Color Values to Terminal (Priority: P1)

The system samples pixel colors at predefined coordinates from each captured frame and prints the RGB and HSV values to the terminal console at the configured frame rate.

**Why this priority**: Color values are the basic unit of telemetry for health bar analysis. Terminal output proves the pipeline works end-to-end.

**Independent Test**: Can be tested by feeding a known-color test pattern (e.g., solid red frame), sampling known coordinates, and verifying the printed values match the expected color.

**Acceptance Scenarios**:

1. **Given** a frame is captured, **When** the system samples a pixel at configured coordinates, **Then** the RGB and HSV values are printed to the terminal
2. **Given** multiple sample points are configured, **When** a frame is processed, **Then** all points are sampled and printed in a single batch
3. **Given** sampling is active, **When** the frame rate is 30 FPS, **Then** terminal output updates at the configured rate without accumulating lag

---

### User Story 3 - Configure via JSON Settings (Priority: P2)

The Spout sender name, sampling coordinates, and target FPS are read from a configuration file so the user can change settings without modifying code.

**Why this priority**: Hardcoded values make testing different games or setups tedious. Configuration enables rapid iteration.

**Independent Test**: Can be tested by writing a config file with specific sample points, running the receiver, and verifying the terminal output samples only those points.

**Acceptance Scenarios**:

1. **Given** a config file with Spout sender name "TestPattern", **When** the receiver starts, **Then** it connects to "TestPattern"
2. **Given** a config file with `sample_points: [[100,50], [200,150]]`, **When** frames arrive, **Then** only those two pixel coordinates are sampled and printed
3. **Given** a config file with `target_fps: 60`, **When** running, **Then** frames are processed at approximately 60 FPS

---

### User Story 4 - Draw ROI Rectangles on Screenshot (Priority: P1)

The user uploads a static HUD screenshot, then draws rectangular regions of interest (Health Bar, Timer, Text) by clicking and dragging on the canvas. Each ROI is named, assigned a tool type, and saved to `config.json`.

**Why this priority**: ROI definitions are the foundation for all downstream analysis. Without them, the system doesn't know where to sample.

**Independent Test**: Upload a screenshot, draw 2-3 rectangles, verify coordinates are saved to `config.json` and reloaded correctly.

**Acceptance Scenarios**:

1. **Given** a screenshot is loaded, **When** the user clicks and drags, **Then** a rectangle overlay appears with live coordinate preview
2. **Given** an ROI is drawn, **When** the user clicks "Add ROI", **Then** it appears in the ROI list and on the canvas
3. **Given** ROIs are defined, **When** the user clicks "Save Config", **Then** all ROI data is serialized to `config.json`

---

### User Story 5 - Mirror ROI Coordinates for P2 (Priority: P2)

For symmetric HUD layouts (e.g., fighting games), the user can mirror a P1 ROI to P2 by inverting the X coordinate: `x_p2 = screen_width - x_p1 - width`.

**Why this priority**: Saves manual coordinate entry for mirrored player positions.

**Independent Test**: Create a P1 ROI at x=100, width=200 on a 1920-width screen; mirror produces P2 ROI at x=1620, width=200.

**Acceptance Scenarios**:

1. **Given** a P1 ROI is selected, **When** the user clicks "Mirror to P2", **Then** a new ROI appears with inverted X coordinates
2. **Given** a mirrored ROI is created, **When** saved, **Then** it includes a `mirrored_from` reference to the source ROI

---

### User Story 6 - SETUP/LIVE Mode Toggle (Priority: P1)

The system operates in two modes: SETUP (UI active, canvas renders, ROI drawing enabled) and LIVE (UI minimized, canvas rendering disabled, analysis runs at configured frame skip).

**Why this priority**: LIVE mode eliminates UI rendering overhead, ensuring the analytical loop runs at full performance.

**Independent Test**: Toggle to LIVE mode, verify canvas stops rendering, verify frame skip dropdown controls analysis frequency.

**Acceptance Scenarios**:

1. **Given** the system is in SETUP mode, **When** the user toggles to LIVE, **Then** the canvas stops rendering and analysis begins
2. **Given** the system is in LIVE mode, **When** frame skip is set to 2, **Then** analysis runs on 1 of every 3 frames
3. **Given** the system is in LIVE mode, **When** an ROI analysis threshold is met, **Then** the corresponding OBS action is dispatched

---

### User Story 7 - Select, Move, and Resize Existing ROIs (Priority: P1)

After drawing an ROI, it persists on the canvas. Clicking inside an existing ROI selects it (highlighted border) instead of starting a new drawing. Selected ROIs can be dragged to reposition and resized via edge/corner handles. The right panel updates to show the selected ROI's name and OBS action for editing.

**Why this priority**: Users need precise control over ROI placement after initial drawing. The current behavior (disappearing on click) forces re-drawing, which is inefficient.

**Independent Test**: Draw an ROI, click inside it — it should select (not start new drawing). Drag to move, verify coordinates update. Drag corner to resize, verify dimensions update.

**Acceptance Scenarios**:

1. **Given** an ROI exists on the canvas, **When** the user clicks inside it, **Then** it becomes selected with a highlighted border and no new drawing starts
2. **Given** an ROI is selected, **When** the user drags it, **Then** the ROI moves and coordinates update in real-time in the right panel
3. **Given** an ROI is selected, **When** the user drags an edge or corner handle, **Then** the ROI resizes and dimensions update in real-time
4. **Given** an ROI is selected, **When** the user clicks outside it, **Then** it deselects and clicking on empty canvas starts a new drawing

---

### User Story 8 - Canvas with 16:9 Aspect Ratio and Signal Scaling (Priority: P1)

The central canvas maintains a fixed 16:9 aspect ratio regardless of window size. Users can scale the received Spout signal to 1080p (1920×1080), 720p (1280×720), or native resolution. The canvas displays the scaled video feed with ROI overlays rendered on top.

**Why this priority**: Consistent aspect ratio ensures ROI coordinates map correctly to the game frame. Scaling options accommodate different capture resolutions.

**Independent Test**: Set canvas to 720p mode, verify it renders at 1280×720 aspect ratio. Switch to 1080p, verify 1920×1080. Verify ROI overlays remain correctly positioned after scale change.

**Acceptance Scenarios**:

1. **Given** the canvas is active, **When** the user selects 720p, **Then** the canvas scales to 16:9 ratio matching 1280×720
2. **Given** the canvas is in 1080p mode, **When** the user switches to 720p, **Then** the video feed and ROI overlays rescale proportionally
3. **Given** the canvas is in LIVE mode, **When** frames arrive, **Then** the video feed is visible through the canvas with ROI overlays rendered on top (not acting as masks)

---

### User Story 9 - OBS Source and Filter Hierarchy (Priority: P1)

OBS actions are applied to either a source OR a filter on that source, not both simultaneously. The user first selects a source from a populated list of all OBS sources. That source can have a visibility action (show/hide). Optionally, the user can enable a checkbox to list all filters on the selected source, then select a filter and assign a visibility action (enable/disable).

**Why this priority**: OBS actions have a parent-child relationship — filters belong to sources. The current UI incorrectly treats sources and filters as independent targets.

**Independent Test**: Connect to OBS, verify source list populates. Select a source, assign "show" action. Enable filter checkbox, verify filter list populates for that source. Select a filter, assign "enable" action. Save config, verify hierarchy is preserved.

**Acceptance Scenarios**:

1. **Given** OBS is connected, **When** the user opens the source dropdown, **Then** all OBS sources are listed
2. **Given** a source is selected, **When** the user assigns an action, **Then** it applies visibility (show/hide) to that source
3. **Given** a source is selected, **When** the user enables the "List Filters" checkbox, **Then** a filter dropdown appears showing only filters belonging to that source
4. **Given** a filter is selected, **When** the user assigns an action, **Then** it applies visibility (enable/disable) to that filter on the parent source
5. **Given** a source has both a source action and a filter action configured, **When** saved, **Then** the config stores them as separate entries with parent-child relationship

---

### User Story 10 - ROI Tool List Panel with Delete (Priority: P1)

A left panel displays all created ROI tools as a list, each with its name, type badge, and an (X) delete button. Clicking an item in the list selects the corresponding ROI on the canvas. Deleting from the list removes the ROI from the canvas and config.

**Why this priority**: Users need a quick overview of all defined tools and a way to manage them without selecting on canvas.

**Independent Test**: Create 3 ROIs, verify all appear in left panel with (X) buttons. Click one — it selects on canvas. Click (X) — it removes from panel and canvas.

**Acceptance Scenarios**:

1. **Given** ROIs exist, **When** the left panel renders, **Then** each ROI appears as a row with name, type badge, and (X) delete button
2. **Given** the left panel shows ROIs, **When** the user clicks a row, **Then** the corresponding ROI is selected on the canvas
3. **Given** an ROI row is visible, **When** the user clicks (X), **Then** the ROI is removed from the canvas, panel, and config on next save

### Edge Cases

- What happens when the Spout sender name doesn't exist? The receiver should log an error and retry periodically, not crash.
- What happens if a sample coordinate is out of frame bounds? The system should clamp to frame edges or skip that sample with a warning.
- What happens when frame resolution changes mid-stream? The receiver should detect the change and re-allocate buffers.
- What happens when the GPU has no Spout-compatible driver? The receiver should fail with a descriptive error on startup.
- What happens when the system can't keep up with the target FPS? The receiver should drop frames rather than queue them unbounded.
- What happens when the user clicks on an ROI boundary (edge/corner)? The system should prioritize resize over move, and move over new drawing.
- What happens when the OBS source list is empty? The system should show "No sources found" placeholder and disable filter checkbox.
- What happens when a selected source has no filters? The filter dropdown should show "No filters" and remain disabled.
- What happens when the canvas is resized during LIVE mode? The video feed and ROI overlays must rescale proportionally without coordinate drift.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST connect to a Spout sender by name and receive frames from GPU VRAM.
- **FR-002**: The system MUST expose each captured frame as a NumPy array in RGBA format.
- **FR-003**: The system MUST sample pixel color values at user-configured coordinates from each frame.
- **FR-004**: The system MUST print sampled RGB and HSV values to the terminal console.
- **FR-005**: The system MUST process frames at a user-configured target frame rate (default: 30 FPS).
- **FR-006**: The system MUST detect Spout sender disconnection and log the event without crashing.
- **FR-007**: The system MUST read Spout sender name, sample points, and target FPS from a configuration file.
- **FR-008**: The system MUST gracefully handle out-of-bounds sample coordinates by clamping or warning.
- **FR-009**: The system MUST detect frame resolution changes mid-stream and adapt.
- **FR-010**: The system MUST provide an interactive canvas for uploading a screenshot and drawing ROI rectangles via mouse drag.
- **FR-011**: The system MUST support three ROI tool types: Health Bar (multi-color sampling), Timer (OCR), and Text (OCR).
- **FR-012**: The system MUST serialize ROI definitions (id, name, x, y, width, height, tool_type, player, obs_target with hierarchical type/source/name/action) to `config.json`.
- **FR-013**: The system MUST mirror P1 ROI coordinates to P2 using the formula: `x_p2 = screen_width - x_p1 - width`.
- **FR-014**: The system MUST operate in SETUP mode (UI active, canvas rendering) and LIVE mode (canvas disabled, analysis only).
- **FR-015**: The system MUST support frame skipping (0-10) in LIVE mode to control analysis frequency.
- **FR-016**: The system MUST dispatch OBS WebSocket actions (visibility toggle, filter enable/disable) when ROI analysis thresholds are met.
- **FR-017**: The system MUST allow selecting existing ROIs by clicking inside them, preventing new drawing when an ROI is clicked.
- **FR-018**: The system MUST allow dragging selected ROIs to reposition them, with live coordinate updates in the properties panel.
- **FR-019**: The system MUST allow resizing selected ROIs via edge/corner drag handles, with live dimension updates in the properties panel.
- **FR-020**: The system MUST maintain a fixed 16:9 aspect ratio for the central canvas regardless of window size.
- **FR-021**: The system MUST provide signal scaling options: native, 1080p (1920×1080), and 720p (1280×720).
- **FR-022**: The system MUST display the live video feed through the canvas in LIVE mode with ROI overlays rendered on top (not as masks).
- **FR-023**: The system MUST list all OBS sources in a dropdown for action assignment, with visibility actions (show/hide) applied to the selected source.
- **FR-024**: The system MUST provide an optional checkbox to list filters belonging to a selected source, with visibility actions (enable/disable) applied to the selected filter.
- **FR-025**: The system MUST display all created ROIs in a left panel list with name, type badge, and (X) delete button per item.
- **FR-026**: The system MUST select the corresponding ROI on the canvas when clicking its entry in the left panel list.

### Key Entities *(include if feature involves data)*

- **SpoutFrame**: A single video frame received from the Spout sender, represented as a NumPy array (height × width × 4 channels, RGBA format).
- **SpoutReceiver**: The component that manages the Spout connection lifecycle — connect, receive, disconnect, reconnect.
- **ColorSample**: A single pixel color reading at a given (x, y) coordinate, containing RGB and HSV values.
- **CaptureConfig**: Configuration specifying the Spout sender name, sample point coordinates, and target processing FPS.
- **ROI**: A rectangular region of interest defined by (x, y, width, height) with a tool_type (health_bar, timer, text), player assignment (1 or 2), OBS action mapping, and optional mirror reference. ROIs are selectable, movable, and resizable on the canvas.
- **AnalysisResult**: The output of an ROI analysis — ROI name, tool type, computed value (fill %, OCR text, etc.), and timestamp.
- **OBSSource**: An OBS scene item or input that can have visibility actions (show/hide) applied. Sources may contain filters.
- **OBSFilter**: A filter attached to a parent OBS source, with independent visibility actions (enable/disable). Filters are listed only after a parent source is selected.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Frames are received and processed at 30 FPS on a mid-range gaming PC with zero frame drops for 10 continuous minutes.
- **SC-002**: Color values printed to terminal match the actual pixel color within ±1 value per channel (verified against a known test pattern).
- **SC-003**: The system survives a Spout sender restart (stop → start) without crashing and resumes frame capture within 2 seconds.
- **SC-004**: Configuration changes (sender name, sample points) take effect on the next startup without code changes.
- **SC-005**: The system consumes less than 5% CPU when idle (connected, no frame changes).
- **SC-006**: ROI drawing workflow: user can upload a screenshot, draw 3 ROIs, assign names and tool types, and save to `config.json` in under 60 seconds.
- **SC-007**: LIVE mode canvas rendering is fully disabled; frame grab + analysis loop runs at configured frame skip with zero PIL/tkinter overhead.
- **SC-008**: OBS WebSocket actions dispatch within 100ms of ROI analysis threshold detection.
- **SC-009**: ROI selection: clicking inside an existing ROI selects it in under 50ms with no new drawing initiated.
- **SC-010**: Canvas maintains exact 16:9 aspect ratio at all window sizes; scaling between 1080p/720p/native completes in under 200ms.
- **SC-011**: Live video feed is fully visible through the canvas in LIVE mode; ROI overlays are semi-transparent and do not obscure the underlying frame.
- **SC-012**: OBS source list populates within 2 seconds of connection; filter list populates within 500ms of enabling the filter checkbox.

## Assumptions

- OBS Studio or another Spout-compatible application is running and broadcasting a Spout sender.
- The system has a DirectX 11 compatible GPU with up-to-date drivers (Spout requirement).
- Development and testing are on Windows (Spout is Windows-only).
- The Spout sender name is known and matches the configured value.
- Sample coordinates are provided as absolute pixel positions matching the sender's resolution.
- The CustomTkinter GUI is used for configuration only; at runtime the UI may be minimized.
- OBS WebSocket v5 is available at `127.0.0.1:4455` by default.
- Center guide line is fixed at X=960 (assuming 1920 screen width).
