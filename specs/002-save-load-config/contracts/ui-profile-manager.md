# Contract: ProfileManager UI Component

The profile management UI is a set of CustomTkinter components that call the
`ProfileManager` API.

## Components

### `ProfileListFrame(ctk.CTkFrame)`

A scrollable list of saved profiles with click-to-select.

```
┌──────────────────────────┐
│  Saved Profiles          │
│                          │
│  ┌────────────────────┐  │
│  │ Street Fighter 6   │  │  ← selected
│  ├────────────────────┤  │
│  │ Tekken 8           │  │
│  ├────────────────────┤  │
│  │ Guilty Gear Strive │  │
│  └────────────────────┘  │
│                          │
│  [Load] [Rename] [Del]   │
│  [Duplicate] [Export]    │
│                          │
│  [Save As...] [Import]   │
└──────────────────────────┘
```

**States**:
- **Empty**: Shows "No saved profiles — configure your first game and click
  Save As" with a prominent [Save Current As...] button.
- **Populated**: Shows profile list with action buttons.
- **Loading**: Disabled buttons, "Loading..." overlay during file operations.
- **Error**: Inline error message for corrupted profiles (with [Delete] option).

### `SaveAsDialog(ctk.CTkToplevel)`

Modal dialog for saving a new profile or overwriting an existing one.

| Field | Control | Validation |
|---|---|---|
| Profile name | `ctk.CTkEntry` | Required, 1–128 chars |
| Overwrite warning | `ctk.CTkLabel` | Shows if name already exists |
| [Cancel] | Button | Closes dialog, no action |
| [Save] | Button | Validates, calls ProfileManager.save() |

### `ImportDialog(ctk.CTkFileDialog)`

File picker for importing a profile.

- Filter: `*.json`
- On file selected: validates JSON, loads into profile list
- On conflict: prompts rename or cancel

## User Flows

### Save Current As
1. User clicks [Save Current As...]
2. `SaveAsDialog` opens with the current game name pre-filled
3. User types/confirms name, clicks [Save]
4. If name exists: warning shown, user confirms overwrite
5. ProfileManager.save() called
6. ProfileListFrame refreshes, new profile auto-selected

### Load Profile
1. User selects a profile in the list
2. User clicks [Load]
3. ProfileManager.load() called
4. If OBS credentials differ: reconnection prompt shown
5. Config applied to all components
6. ProfileListFrame highlights loaded profile

### Import
1. User clicks [Import]
2. File picker opens, filtered to `.json`
3. File selected → validation
4. On success: profile added, list refreshed
5. On conflict: "Profile 'X' already exists. Import as 'X (imported)'?"

### Export
1. User selects a profile, clicks [Export]
2. Save file dialog opens (default: `<profile-name>.json`)
3. ProfileManager.export() called
4. Success confirmation shown
