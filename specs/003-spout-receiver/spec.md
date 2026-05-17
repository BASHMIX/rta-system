# Feature Specification: Spout Frame Receiver

**Feature Branch**: `003-spout-receiver`

**Created**: 2026-05-17

**Status**: Draft

**Input**: User description: "Spout receiver that captures frames and prints color values to terminal"

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

### Edge Cases

- What happens when the Spout sender name doesn't exist? The receiver should log an error and retry periodically, not crash.
- What happens if a sample coordinate is out of frame bounds? The system should clamp to frame edges or skip that sample with a warning.
- What happens when frame resolution changes mid-stream? The receiver should detect the change and re-allocate buffers.
- What happens when the GPU has no Spout-compatible driver? The receiver should fail with a descriptive error on startup.
- What happens when the system can't keep up with the target FPS? The receiver should drop frames rather than queue them unbounded.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST connect to a Spout sender by name and receive frames from GPU VRAM.
- **FR-002**: The system MUST expose each captured frame as a NumPy array in BGRA (or RGB) format.
- **FR-003**: The system MUST sample pixel color values at user-configured coordinates from each frame.
- **FR-004**: The system MUST print sampled RGB and HSV values to the terminal console.
- **FR-005**: The system MUST process frames at a user-configured target frame rate (default: 30 FPS).
- **FR-006**: The system MUST detect Spout sender disconnection and log the event without crashing.
- **FR-007**: The system MUST read Spout sender name, sample points, and target FPS from a configuration file.
- **FR-008**: The system MUST gracefully handle out-of-bounds sample coordinates by clamping or warning.
- **FR-009**: The system MUST detect frame resolution changes mid-stream and adapt.

### Key Entities *(include if feature involves data)*

- **SpoutFrame**: A single video frame received from the Spout sender, represented as a NumPy array (height × width × 4 channels).
- **SpoutReceiver**: The component that manages the Spout connection lifecycle — connect, receive, disconnect, reconnect.
- **ColorSample**: A single pixel color reading at a given (x, y) coordinate, containing RGB and HSV values.
- **CaptureConfig**: Configuration specifying the Spout sender name, sample point coordinates, and target processing FPS.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Frames are received and processed at 30 FPS on a mid-range gaming PC with zero frame drops for 10 continuous minutes.
- **SC-002**: Color values printed to terminal match the actual pixel color within ±1 value per channel (verified against a known test pattern).
- **SC-003**: The system survives a Spout sender restart (stop → start) without crashing and resumes frame capture within 2 seconds.
- **SC-004**: Configuration changes (sender name, sample points) take effect on the next startup without code changes.
- **SC-005**: The system consumes less than 5% CPU when idle (connected, no frame changes).

## Assumptions

- OBS Studio or another Spout-compatible application is running and broadcasting a Spout sender.
- The system has a DirectX 11 compatible GPU with up-to-date drivers (Spout requirement).
- Development and testing are on Windows (Spout is Windows-only).
- The Spout sender name is known and matches the configured value.
- No UI is needed for this sprint — all output is via terminal/console.
- Sample coordinates are provided as absolute pixel positions matching the sender's resolution.
