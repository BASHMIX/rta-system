# Tasks: Spout Frame Receiver

**Input**: Design documents from `specs/003-spout-receiver/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: No explicit test tasks unless requested.

**Organization**: Tasks are grouped by user story to enable independent implementation.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create directory structure: src/spout/, tests/
- [x] T001a Create sample config.json at project root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities that ALL user stories depend on

- [x] T002 [P] Create SpoutFrame data class with width, height, data (ndarray), timestamp in src/spout/receiver.py
- [x] T003 Create FrameSource ABC with open/close/grab/is_open/frame_width/frame_height in src/spout/receiver.py
- [x] T004 Create ColorSample dataclass with x, y, r, g, b, h, s, v in src/spout/sampler.py
- [x] T005 Create SpoutConfig dataclass with sender_name, sample_points, target_fps in src/spout/config.py
- [x] T006 Create throttle utility function in src/utils.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Capture Frames from a Spout Sender (Priority: P1) 🎯 MVP

**Goal**: Connect to a Spout sender and receive live video frames as NumPy arrays.

**Independent Test**: Run with OBS Spout output active; verify frames arrive at expected resolution.

- [x] T007 [US1] Implement SpoutGLSource (FrameSource) in src/spout/receiver.py (initially had broken receiveImage API — fixed in T021)
- [x] T008 [US1] Create run.py terminal entry point with capture loop in src/spout/run.py

**Checkpoint**: At this point, US1 should work - frames captured from Spout sender.

---

## Phase 4: User Story 2 - Print Color Values to Terminal (Priority: P1)

**Goal**: Sample pixel colors at configured coordinates and print RGB/HSV to terminal.

**Independent Test**: Run against known test pattern; verify printed values match expected colors.

- [x] T009 [US2] Create sample_pixel() function with coordinate clamping in src/spout/sampler.py
- [x] T010 [US2] Create create_sample_batch() that samples all configured points in src/spout/sampler.py
- [x] T011 [US2] Add color conversion helpers (BGRA→RGB, RGB→HSV) in src/utils.py
- [x] T012 [US2] Integrate sampling + terminal printing into main.py capture loop

**Checkpoint**: US1 + US2 both work - frames captured, colors sampled and printed to terminal.

---

## Phase 5: User Story 3 - Configure via JSON Settings (Priority: P2)

**Goal**: Spout sender name, sample points, and target FPS read from config.json.

**Independent Test**: Change config.json values and restart; verify new settings take effect.

- [x] T013 [US3] Implement SpoutConfig.from_file() to load from config.json in src/spout/config.py
- [x] T014 [US3] Implement config validation with descriptive error messages in src/spout/config.py
- [x] T015 [US3] Wire config loading into main.py entry point

**Checkpoint**: All 3 user stories functional - fully configurable via config.json.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, logging, reconnection logic, edge cases.

- [x] T016 Setup Python logging with console handler in src/utils.py
- [x] T017 Add graceful Spout disconnection detection and reconnection in src/spout/receiver.py
- [x] T018 Add sender resolution change detection in src/spout/receiver.py
- [x] T019 Add frame drop detection when system can't keep up in main.py
- [x] T020 Add config.json error handling for missing/invalid files in main.py

---

## Phase 7: Workspace UI & Bug Fixes

**Purpose**: Fix Spout capture bug, add sender discovery UI, replace widget UI.

- [x] T021 Fix SpoutGLSource.receiveImage() API — pre-allocate bytearray, call receiveImage(buffer, GL_BGRA_EXT, False, 0), check bool return
- [x] T022 Add get_available_senders() and set_sender() methods in src/spout/receiver.py
- [x] T023 Fix close() to call releaseReceiver() before nulling in src/spout/receiver.py
- [x] T024 Use .copy() on frame data to avoid buffer corruption in src/spout/receiver.py
- [x] T025 Create ToggleGroup radio widget in src/ui/widgets/toggle_group.py
- [x] T026 Create ConnectionRow widget (label + dropdown + status dot) in src/ui/widgets/connection_row.py
- [x] T027 Create ToolsPanel (left column) in src/ui/tools_panel.py
- [x] T028 Create Workspace panel (center column) in src/ui/workspace.py
- [x] T029 Create PropertiesPanel (right column) in src/ui/properties.py
- [x] T030 Create RTAWorkspace 3-column app layout in src/ui/app.py
- [x] T031 Replace main.py with new RTAWorkspace entry point
- [x] T032 Create OBSClient stub in src/obs/client.py
- [x] T033 Clean up plan.md NEEDS CLARIFICATION markers and source file count

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup
- **US1 (Phase 3)**: Depends on Foundational
- **US2 (Phase 4)**: Depends on Foundational; can run after/before US1
- **US3 (Phase 5)**: Depends on Foundational; integrates with US1/US2
- **Polish (Phase 6)**: Depends on all phases

### Parallel Opportunities

- T002, T003, T004, T005, T006 can all run in parallel
- T009, T010, T011 can run in parallel

---

## Implementation Strategy

### MVP First (US1 Only)

1. Phase 1: Setup
2. Phase 2: Foundational
3. Phase 3: US1 → Frames captured (MVP!)
4. Phase 4: US2 → Color values printed to terminal
5. Phase 5: US3 → Config from JSON
6. Phase 6: Polish → Robust error handling
