# Feature Specification: Spout Frame Receiver

**Feature Branch**: `003-spout-receiver`

**Created**: 2026-05-17

**Status**: Draft

**Input**: User description: "Spout receiver that captures frames and prints color values to terminal"

**Clarification 2026-05-17**: Scope expanded from terminal-only (Sprint 1) to include Phase 1 UI & Drawing Tools (Sprint 3 frontend): interactive screenshot workspace, ROI rectangle drawing, custom naming, OBS action assignment, P2 mirroring, and `config.json` export.

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

### Edge Cases

- What happens when the Spout sender name doesn't exist? The receiver should log an error and retry periodically, not crash.
- What happens if a sample coordinate is out of frame bounds? The system should clamp to frame edges or skip that sample with a warning.
- What happens when frame resolution changes mid-stream? The receiver should detect the change and re-allocate buffers.
- What happens when the GPU has no Spout-compatible driver? The receiver should fail with a descriptive error on startup.
- What happens when the system can't keep up with the target FPS? The receiver should drop frames rather than queue them unbounded.

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
- **FR-012**: The system MUST serialize ROI definitions (id, name, x, y, width, height, tool_type, player, obs_source, obs_filter, obs_action) to `config.json`.
- **FR-013**: The system MUST mirror P1 ROI coordinates to P2 using the formula: `x_p2 = screen_width - x_p1 - width`.
- **FR-014**: The system MUST operate in SETUP mode (UI active, canvas rendering) and LIVE mode (canvas disabled, analysis only).
- **FR-015**: The system MUST support frame skipping (0-10) in LIVE mode to control analysis frequency.
- **FR-016**: The system MUST dispatch OBS WebSocket actions (visibility toggle, filter enable/disable) when ROI analysis thresholds are met.

### Key Entities *(include if feature involves data)*

- **SpoutFrame**: A single video frame received from the Spout sender, represented as a NumPy array (height × width × 4 channels, RGBA format).
- **SpoutReceiver**: The component that manages the Spout connection lifecycle — connect, receive, disconnect, reconnect.
- **ColorSample**: A single pixel color reading at a given (x, y) coordinate, containing RGB and HSV values.
- **CaptureConfig**: Configuration specifying the Spout sender name, sample point coordinates, and target processing FPS.
- **ROI**: A rectangular region of interest defined by (x, y, width, height) with a tool_type (health_bar, timer, text), player assignment (1 or 2), OBS action mapping, and optional mirror reference.
- **AnalysisResult**: The output of an ROI analysis — ROI name, tool type, computed value (fill %, OCR text, etc.), and timestamp.

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

## Assumptions

- OBS Studio or another Spout-compatible application is running and broadcasting a Spout sender.
- The system has a DirectX 11 compatible GPU with up-to-date drivers (Spout requirement).
- Development and testing are on Windows (Spout is Windows-only).
- The Spout sender name is known and matches the configured value.
- Sample coordinates are provided as absolute pixel positions matching the sender's resolution.
- The CustomTkinter GUI is used for configuration only; at runtime the UI may be minimized.
- OBS WebSocket v5 is available at `127.0.0.1:4455` by default.
- Center guide line is fixed at X=960 (assuming 1920 screen width).
