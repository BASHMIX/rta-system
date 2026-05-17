# Tasks: Save & Load Game Configs

**Input**: Design documents from `specs/002-save-load-config/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths follow the plan.md structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project skeleton with `src/` and `tests/` directories, `src/__init__.py`, and `src/config/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 [P] Create GameProfile, ProfileEntry, and ProfileIndex data classes in `src/config/models.py`
- [x] T003 [P] Create JSON schema validation (profile-schema.md) in `src/config/schema.py`
- [x] T004 Create ProfileManager core with profiles/ directory init and index.json management in `src/config/profiles.py`
- [x] T005 Create test conftest.py with temp directory fixture in `tests/conftest.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Save Current Configuration as a Game Profile (Priority: P1) 🎯 MVP

**Goal**: Users can save their full configuration as a named game profile

**Independent Test**: Complete an ROI configuration, click "Save As", enter a profile name, close the app, and verify the profile file exists in the `profiles/` directory

- [x] T006 [P] [US1] Implement save() method in `src/config/profiles.py` to write GameProfile to JSON file and update index
- [x] T007 [P] [US1] Implement confirm_overwrite() method in `src/config/profiles.py` to check for name collisions
- [x] T008 [US1] Create SaveAsDialog UI component in `src/ui/profile_manager.py` with name entry, overwrite warning, and Save/Cancel buttons

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Load a Game Profile (Priority: P1)

**Goal**: Users can load a saved game profile, replacing all current configuration

**Independent Test**: Save two distinct configurations, load each one, and verify ROIs, rules, and settings match what was saved

- [x] T009 [P] [US2] Implement load() method in `src/config/profiles.py` to read and validate a GameProfile from JSON
- [x] T010 [P] [US2] Implement get_profile_summary() and profile_names property in `src/config/profiles.py` for list display
- [x] T011 [US2] Create ProfileListFrame UI component in `src/ui/profile_manager.py` with scrollable profile list and Load/action buttons
- [x] T012 [US2] Implement auto-load last-used profile on app startup using index.json last_loaded field

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Manage Game Profiles (Priority: P2)

**Goal**: Users can rename, delete, and duplicate existing game profiles

**Independent Test**: Create multiple profiles, rename one, delete another, duplicate a third, then verify the list reflects each operation

- [x] T013 [P] [US3] Implement rename() method in `src/config/profiles.py` to rename a profile on disk and in index
- [x] T014 [P] [US3] Implement delete() method in `src/config/profiles.py` to remove a profile file and index entry
- [x] T015 [P] [US3] Implement duplicate() method in `src/config/profiles.py` to copy a profile with a suffix
- [x] T016 [US3] Wire Rename, Delete, and Duplicate buttons in ProfileListFrame in `src/ui/profile_manager.py`

**Checkpoint**: At this point, User Stories 1, 2, AND 3 work independently

---

## Phase 6: User Story 4 - Import and Export Profiles (Priority: P3)

**Goal**: Users can export profiles to standalone files and import profiles from external files

**Independent Test**: Export a profile, delete it, import it back, and verify all settings match the original

- [x] T017 [P] [US4] Implement export() method in `src/config/profiles.py` to copy a profile file to an external path
- [x] T018 [P] [US4] Implement import_() method in `src/config/profiles.py` to validate and import a profile file with name conflict resolution
- [x] T019 [US4] Create ImportDialog (file picker + validation) and Export button handler in `src/ui/profile_manager.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T020 [P] Handle corrupted profile detection on load — ValueError with descriptive message, inline error in ProfileListFrame
- [x] T021 [P] Implement OBS credential diff check on profile load in `src/config/profiles.py` with reconnection prompt in UI
- [x] T022 [P] Add threading.Lock to ProfileManager for safe concurrent file I/O
- [x] T023 Update AGENTS.md, quickstart.md, and run quickstart validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 (save) has no dependency on other stories
  - US2 (load) depends on US1 save() being complete (needs profiles to load)
  - US3 (manage) depends on US2 load() (needs profile list)
  - US4 (import/export) depends on US3 (needs profile management UI)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Depends on US1 (save creates profiles that load reads)
- **User Story 3 (P2)**: Depends on US2 (load populates profile list)
- **User Story 4 (P3)**: Depends on US3 (import/export uses management UI)

### Within Each User Story

- Models before services
- Core logic (profiles.py) before UI (profile_manager.py)
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel
- [P] tasks within each user story can run in parallel (models, services, core logic)

---

## Parallel Example: User Story 1

```bash
# Launch all core logic tasks for US1 together:
Task: "Implement save() in src/config/profiles.py"
Task: "Implement confirm_overwrite() in src/config/profiles.py"

# Then launch UI (depends on save being complete):
Task: "Create SaveAsDialog UI component in src/ui/profile_manager.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Save)
4. **STOP and VALIDATE**: User can save a profile and verify it persists
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Save) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (Load) → Test independently → Deploy/Demo
4. Add User Story 3 (Manage) → Test independently → Deploy/Demo
5. Add User Story 4 (Import/Export) → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
