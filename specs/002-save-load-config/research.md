# Research: Save & Load Game Configs

No NEEDS CLARIFICATION markers were raised in Technical Context. All decisions
resolved from the roadmap, constitution, and reasonable defaults.

## Decisions

### Profile Storage Format
**Decision**: Individual JSON files in `profiles/` directory.
**Rationale**: Extends the roadmap's `config.json` pattern (Constitution II).
Each profile is a complete config snapshot. Individual files allow independent
read/write without cross-file corruption risk.
**Alternatives considered**: Single multi-profile JSON file (rejected: higher
corruption blast radius, harder to import/export individual profiles). SQLite
(rejected: overkill for single-user local file storage).

### Profile Directory Location
**Decision**: `profiles/` at project root, with a `profiles/` entry in
`.gitignore`.
**Rationale**: Keeps profiles separate from source code. User-created data
should not be tracked in version control.
**Alternatives considered**: App data directory (`%APPDATA%`) — deferred to
post-v1 packaging. Relative to config file — profiles are an extension of
the config pattern.

### Profile File Naming
**Decision**: Sanitized profile name as filename (`profiles/<sanitized-name>.json`),
with a sidecar `profiles/index.json` for display-order metadata.
**Rationale**: File system lookup is fast. Index file preserves user-defined
display order and last-used timestamp.
**Alternatives considered**: Directory per profile (rejected: unnecessary nesting).
UUID filenames with name index (rejected: adds complexity without benefit for
single-user local storage).

### Concurrency Safety
**Decision**: Use a threading lock (`threading.Lock`) around profile file
operations. The monitoring worker reads config at startup and on profile
switch — it does not write profiles.
**Rationale**: Simple, sufficient for single-user scenario. Writer-writer
conflicts only happen if user rapidly saves twice, which the lock handles.
**Alternatives considered**: File-level locking (overkill for single user).
Queue-based writes (premature optimization).

### OBS Reconnection on Profile Switch
**Decision**: Compare OBS WebSocket credentials on profile load. If host, port,
or password differ, prompt user for reconnection. If identical, keep existing
connection.
**Rationale**: Avoids unnecessary OBS disconnection. The reconnection prompt
gives the user control.
**Alternatives considered**: Always reconnect (disruptive if credentials unchanged).
Silent reconnect (confusing if connection drops unexpectedly).

### Import/Export Format
**Decision**: Single `.json` file — same internal format as profile files.
User can rename the exported file for sharing.
**Rationale**: Zero transformation overhead. No custom format to document.
**Alternatives considered**: ZIP with metadata (overkill for a single JSON file).
Encrypted format (out of scope for v1 — no security requirements).
