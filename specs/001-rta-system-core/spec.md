# Feature Specification: RTA System Core

**Feature Branch**: `001-rta-system-core`

**Created**: 2026-05-17

**Status**: Draft

**Input**: User description: "The Real-Time FGC Telemetry & OBS Automation (RTA) system is a lightweight, local program that runs in the background to read the real-time gameplay of fighting games directly from the graphics card's VRAM via the Spout protocol without any performance loss..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configure HUD Regions of Interest (Priority: P1)

A streamer opens the RTA application for the first time, sees a live preview of their game feed, and draws bounding boxes around key HUD elements (health bar, combo counter, warning text). They assign a type label and basic parameters to each box.

**Why this priority**: Without ROI configuration, no telemetry can be extracted. This is the foundational setup flow.

**Independent Test**: Can be fully tested by launching the app with a static test image, drawing a rectangle over a colored region, and verifying the box coordinates are saved.

**Acceptance Scenarios**:

1. **Given** the app is running with a live Spout feed, **When** the user clicks and drags on the preview canvas, **Then** a rectangular bounding box appears and follows the cursor
2. **Given** a bounding box is drawn, **When** the user selects an element type from the dropdown, **Then** the box is labeled accordingly in the configuration panel
3. **Given** all ROIs are configured, **When** the user clicks "Save Configuration", **Then** all ROI coordinates, types, and parameters are persisted to a configuration file

---

### User Story 2 - Real-Time Telemetry Monitoring (Priority: P1)

After configuration, the user switches to monitoring mode. The system reads frames from the GPU, crops each ROI, and extracts game state data (health percentage from bar fill, combo counter value, warning text presence). Results are displayed in real-time.

**Why this priority**: This is the core analytical capability that drives all downstream OBS automation.

**Independent Test**: Can be tested by feeding a known test image sequence and verifying the extracted values match expected ground truth (e.g., a health bar at 50% fill reports 50%).

**Acceptance Scenarios**:

1. **Given** the system is in monitoring mode, **When** a frame arrives via Spout, **Then** each ROI is cropped and analyzed within the target frame time
2. **Given** a health bar ROI is configured, **When** the bar fill percentage changes, **Then** the current percentage updates in the monitoring display
3. **Given** a text zone ROI is configured, **When** the text content changes (e.g., "Counter Attack" appears), **Then** the system registers the text state change

---

### User Story 3 - OBS Automation via Detected Events (Priority: P1)

When the system detects a dramatic game event (health dropping below 25%, a "Counter Attack" prompt appearing), it automatically triggers OBS via WebSocket to show/hide overlays, apply color filters, or play audio clips on the live stream.

**Why this priority**: OBS automation is the primary output of the system — without it, the telemetry has no live-stream application.

**Independent Test**: Can be tested by simulating a game event (e.g., changing a test image to show low health) and verifying the OBS WebSocket receives the correct command.

**Acceptance Scenarios**:

1. **Given** the system detects health below 25%, **When** the event is evaluated against configured rules, **Then** OBS receives a command to toggle a "danger" overlay source visible
2. **Given** the system detects a "Counter Attack" text event, **When** the event fires, **Then** OBS receives a command to activate an impact flash filter
3. **Given** a dramatic event ends, **When** the condition no longer applies, **Then** OBS receives a command to restore the prior visual state

---

### User Story 4 - P1-to-P2 Mirror Configuration (Priority: P2)

The user has configured ROIs for Player 1 and wants to duplicate them for Player 2 with mirrored coordinates. They click "Mirror P1 to P2" and the system automatically generates the inverse coordinates and flips depletion directions.

**Why this priority**: Fighting games are two-player; manually re-drawing the same boxes for the second player wastes time and introduces inconsistency.

**Independent Test**: Can be tested by configuring P1 ROIs, clicking mirror, and verifying P2 ROIs have correct screen-width-inverted coordinates.

**Acceptance Scenarios**:

1. **Given** P1 ROIs are configured, **When** the user clicks "Mirror P1 to P2", **Then** P2 ROIs are created with X coordinates inverted by screen width
2. **Given** a P1 health bar has a right-to-left depletion direction, **When** mirrored, **Then** the P2 health bar direction is set to left-to-right

---

### User Story 5 - Event Rule Configuration (Priority: P3)

The user defines custom condition-action rules: specific telemetry conditions paired with specific OBS actions. For example, "when P1 health drops below 25%, show the red vignette overlay and enable the danger color correction filter."

**Why this priority**: Preset default rules enable immediate use, but custom rules are needed for advanced users to tailor the system to their specific stream setup.

**Independent Test**: Can be tested by defining a custom rule and verifying it triggers the correct OBS action when the condition is met.

**Acceptance Scenarios**:

1. **Given** the event rules panel, **When** the user creates a new rule with a condition and an action, **Then** the rule is added to the active rules list
2. **Given** multiple rules exist, **When** a single game event triggers multiple conditions, **Then** all matching rules execute their actions in configured order

### Edge Cases

- What happens when the Spout feed disconnects mid-monitoring? The system should detect the lost signal and pause analysis, displaying a "Feed Lost" indicator, then auto-resume when the feed returns.
- How does the system handle a player being at exactly 0% or 100% health? Both boundaries must be reported correctly without divide-by-zero or rounding errors.
- What happens when OBS WebSocket is unreachable? OBS actions should be queued or skipped with a clear warning, but telemetry monitoring should continue unaffected.
- How are overlapping ROIs handled? If two drawn boxes overlap, the system should warn the user and let them decide which takes priority.
- What happens when the game resolution changes? The configuration stores ROIs in absolute pixels; the system should detect resolution changes and prompt the user to re-validate ROIs.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST capture live game frames from GPU video memory at full source framerate with zero measurable CPU overhead for frame copy.
- **FR-002**: Users MUST be able to draw rectangular bounding boxes on a live preview canvas to define Regions of Interest.
- **FR-003**: Users MUST be able to assign an element type label to each ROI from a predefined set (health bar, combo counter, system text).
- **FR-004**: The system MUST crop each ROI from the captured frame and analyze its content based on element type.
- **FR-005**: For health bar ROIs, the system MUST calculate the fill percentage by isolating the bar color and measuring the filled-to-total ratio.
- **FR-006**: For text zone ROIs, the system MUST detect significant pixel density changes indicating new text appearing or disappearing.
- **FR-007**: The system MUST support right-to-left and left-to-right depletion direction configuration for health bars.
- **FR-008**: The system MUST support segment count configuration for health bars (e.g., 4 segments per bar).
- **FR-009**: The system MUST connect to OBS via WebSocket and toggle scene item visibility and source filter states.
- **FR-010**: Users MUST be able to define condition-action rules mapping telemetry events to OBS actions.
- **FR-011**: The system MUST support a "Mirror P1 to P2" operation that inverts ROI X coordinates across screen width and flips depletion direction.
- **FR-012**: The system MUST persist all configuration to a reloadable file that loads at startup.
- **FR-013**: The monitoring loop MUST run in a background thread so the UI remains responsive.
- **FR-014**: The system MUST detect Spout feed disconnection and display a visual indicator.

### Key Entities *(include if feature involves data)*

- **Capture Source**: The live game video stream received via Spout protocol. Provides frames for analysis.
- **Region of Interest (ROI)**: A rectangular area on the captured frame defined by its coordinates (x, y, width, height). Each ROI targets a specific HUD element.
- **Element Type**: The classification label for an ROI - determines the analysis algorithm (health bar, combo counter, system text).
- **Player (P1 / P2)**: A grouping of ROIs belonging to one side. Each player has its own set of ROIs with independent parameters.
- **Telemetry Event**: A detected state change from ROI analysis - e.g., "health dropped to 20%", "Counter Attack text appeared".
- **Condition-Action Rule**: A mapping from a telemetry condition (e.g., "P1 health < 25%") to one or more OBS actions (e.g., toggle source, toggle filter).
- **Configuration**: The complete set of system settings, player ROIs, and condition-action rules persisted as a single file.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can configure ROIs for a fighting game and start telemetry monitoring within 5 minutes of first launch.
- **SC-002**: Frame analysis completes in under 16ms (60 FPS equivalent) for up to 8 active ROIs on a mid-range gaming PC.
- **SC-003**: OBS reactions trigger within 200ms of the corresponding game event occurring on screen.
- **SC-004**: The system adds zero measurable frame time impact to the game being captured (no FPS drop in the game).
- **SC-005**: Configuration files save and reload with 100% identical ROI positions, types, and rule definitions.
- **SC-006**: The P1-to-P2 mirror operation produces correctly inverted coordinates on the first attempt without manual correction.

## Assumptions

- The target platform is Windows (Spout protocol is Windows-only).
- OBS Studio is installed and running with the WebSocket server v5 enabled and a known password.
- The game being captured runs on the same machine and outputs a Spout sender stream.
- The game's HUD layout is consistent throughout a session (no dynamic repositioning of elements).
- The user has basic familiarity with OBS scene/source/filter management for setting up reaction overlays.
- Screen resolution is consistent between configuration and monitoring sessions.
- AI/ML training data collection is a future capability; this initial spec covers real-time telemetry extraction only, not model training.
- A single monitor setup is used for development; multi-monitor support is out of scope for v1.
