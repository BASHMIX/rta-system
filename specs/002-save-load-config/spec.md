# Feature Specification: Save & Load Game Configs

**Feature Branch**: `002-save-load-config`

**Created**: 2026-05-17

**Status**: Draft

**Input**: User description: "add the ability to save and load user configuration for each game"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Save Current Configuration as a Game Profile (Priority: P1)

A streamer has finished configuring ROIs, event rules, and system settings for Street Fighter 6. They click "Save As", type "Street Fighter 6", and the entire setup is persisted under that name.

**Why this priority**: Without saving, every configuration is ephemeral. This is the foundational persistence mechanism.

**Independent Test**: Can be fully tested by completing a full ROI configuration, saving with a profile name, closing the app, and verifying the profile file exists.

**Acceptance Scenarios**:

1. **Given** the user has configured ROIs and rules for a game, **When** they click "Save As" and enter a profile name, **Then** the entire configuration is saved under that name
2. **Given** a profile name already exists, **When** the user attempts to save with the same name, **Then** the system prompts for confirmation before overwriting
3. **Given** a save operation completes, **When** the user inspects the profiles list, **Then** the new profile appears in the list

---

### User Story 2 - Load a Game Profile (Priority: P1)

The streamer wants to switch from Street Fighter 6 to Tekken 8. They open the profile selector, click "Tekken 8", and all ROIs, rules, and settings switch to the Tekken configuration.

**Why this priority**: Loading is the other half of persistence — without it, saved profiles are useless. This is tied with saving as the core value.

**Independent Test**: Can be fully tested by saving two distinct configurations, loading each one, and verifying the ROIs and rules match what was saved.

**Acceptance Scenarios**:

1. **Given** multiple saved profiles exist, **When** the user selects a profile from the list, **Then** all ROIs, rules, and settings are restored to match that profile
2. **Given** a profile is loaded, **When** the user switches to a different profile, **Then** the previous configuration is replaced entirely (no residual ROIs from the prior profile)
3. **Given** the app starts with saved profiles, **When** it launches, **Then** the last-used profile is auto-loaded

---

### User Story 3 - Manage Game Profiles (Priority: P2)

The streamer wants to clean up their profile list — renaming "SF6 Test" to "Street Fighter 6", deleting an outdated "Guilty Gear Strive (old)" profile, and duplicating "Tekken 8" to try experimental settings.

**Why this priority**: Profile management is essential for organization once multiple games are configured, but not required for the initial save/load flow.

**Independent Test**: Can be tested by creating multiple profiles, renaming one, deleting another, and duplicating a third, then verifying the list reflects each operation.

**Acceptance Scenarios**:

1. **Given** a profile exists, **When** the user renames it, **Then** the profile name updates in the list and the saved data retains its integrity
2. **Given** a profile exists, **When** the user deletes it, **Then** the profile is removed from the list and its data is permanently removed
3. **Given** a profile exists, **When** the user duplicates it, **Then** a copy is created with a "Copy" suffix and contains identical settings

---

### User Story 4 - Import and Export Profiles (Priority: P3)

The streamer wants to share their carefully tuned "Street Fighter 6" config with a friend, or restore a backup after reinstalling the app. They export the profile to a file and later import it.

**Why this priority**: Sharing and backup are valuable but non-essential. Most users will reconfigure per-machine rather than transfer configs.

**Independent Test**: Can be tested by exporting a profile, deleting it, importing it back, and verifying all settings match the original.

**Acceptance Scenarios**:

1. **Given** a saved profile exists, **When** the user exports it, **Then** a standalone file is created that can be shared or stored externally
2. **Given** an exported profile file, **When** the user imports it, **Then** the profile appears in the profiles list with all settings intact
3. **Given** an imported profile has the same name as an existing one, **When** imported, **Then** the system appends a suffix or prompts to resolve the conflict

### Edge Cases

- What happens when a profile file is corrupted? The system should detect the corruption and report which profile failed to load, allowing the user to delete or re-import it.
- What happens when the profiles directory is deleted externally? The app should detect the missing directory on startup and create a fresh one, starting with a clean default profile.
- How does the system behave with an empty profile list on first launch? It should show a clear "No saved profiles yet" message and prompt the user to create one.
- What if the user saves while monitoring is active? Saving should capture the current (live) configuration state — any real-time telemetry values are not saved, only the static configuration.
- What happens to the active OBS connection when switching profiles? The system should warn if switching profiles will change OBS WebSocket settings and prompt for reconnection.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to save the entire current configuration (all ROIs, player settings, event rules, and system settings) as a named game profile.
- **FR-002**: Users MUST be able to view a list of all saved game profiles in the UI.
- **FR-003**: Users MUST be able to load any saved game profile, replacing the current configuration entirely.
- **FR-004**: The system MUST auto-load the last-used game profile on application startup.
- **FR-005**: Users MUST be able to rename an existing game profile.
- **FR-006**: Users MUST be able to delete a game profile from the list.
- **FR-007**: Users MUST be able to duplicate an existing game profile under a new name.
- **FR-008**: The system MUST warn the user before overwriting an existing profile with the same name during save.
- **FR-009**: Users MUST be able to export a game profile to a standalone portable file.
- **FR-010**: Users MUST be able to import a game profile from a portable file.
- **FR-011**: The system MUST detect and report corrupted profile files during load, without crashing or affecting other profiles.
- **FR-012**: The system MUST preserve profile data integrity across application restarts — all saved profiles must be available after relaunch.

### Key Entities *(include if feature involves data)*

- **Game Profile**: A named collection of the full system configuration — all ROIs (per player), element type assignments, segment/direction parameters, OBS event rules, and system settings (resolution, WebSocket details). Represents a complete setup for one fighting game title.
- **Profile List**: The set of all saved game profiles visible to the user. Profiles are stored individually and cataloged on startup to populate this list.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can save a completed configuration in under 5 seconds (one click + one text entry).
- **SC-002**: A user can switch between two game configurations in under 3 clicks and under 2 seconds.
- **SC-003**: All profile data survives app restarts with 100% fidelity — ROIs, labels, and rules are identical before and after relaunch.
- **SC-004**: A first-time user with no saved profiles sees an informative empty state (not a blank screen or error).
- **SC-005**: Profile import and export produce files that are portable across machines running the same app version.

## Assumptions

- Each game profile is stored independently (no shared mutation between profiles).
- Profile names are user-defined free-text strings and do not need to match a game title registry.
- The currently active configuration is always the starting point for a "Save As" operation.
- OBS WebSocket credentials (host, port, password) are included in each profile, allowing different OBS setups per game.
- The system supports at least 50 profiles without noticeable performance degradation in the profile list.
- Import/export uses a single-file format that can be shared via email, cloud storage, or USB drive.
