# Contract: ProfileManager API

The `ProfileManager` class is the interface between the UI layer and profile
storage. It owns all profile file I/O and state.

## Class: `ProfileManager`

```python
class ProfileManager:
    def __init__(self, profiles_dir: str | Path = "profiles") -> None
    """
    Initialize manager. Creates profiles_dir if missing.
    Loads index.json or creates empty index.
    """

    @property
    def profile_names(self) -> list[str]
    """Return list of profile names in display order."""

    @property
    def last_loaded_name(self) -> str | None
    """Name of the profile loaded most recently, or None."""

    def save(self, name: str, config: FullConfig) -> GameProfile
    """
    Save a new profile. Raises FileExistsError if name exists
    (caller must confirm overwrite via confirm_overwrite first).
    Returns the saved GameProfile.
    """

    def load(self, name: str) -> GameProfile
    """
    Load a profile by name. Raises FileNotFoundError if not found,
    ValueError if file is corrupted.
    Returns the deserialized GameProfile.
    """

    def rename(self, old_name: str, new_name: str) -> None
    """
    Rename a profile. Updates index and renames file on disk.
    Raises FileNotFoundError, FileExistsError (if new_name taken).
    """

    def delete(self, name: str) -> None
    """
    Delete a profile. Removes from index and deletes file.
    Raises FileNotFoundError if name not found.
    """

    def duplicate(self, name: str, suffix: str = "Copy") -> str
    """
    Duplicate a profile. Appends suffix to name.
    Returns the new profile name.
    Raises FileNotFoundError if source not found.
    """

    def export(self, name: str, target_path: str | Path) -> None
    """
    Export a profile to an external file path.
    Raises FileNotFoundError if profile not found.
    """

    def import_(self, source_path: str | Path) -> str
    """
    Import a profile from an external file. Resolves name conflicts
    by appending a numeric suffix.
    Returns the imported profile name.
    Raises ValueError if file is invalid JSON or fails schema validation.
    """

    def confirm_overwrite(self, name: str) -> bool
    """
    Check if saving as 'name' would overwrite an existing profile.
    Returns True if name exists (caller should prompt user).
    """

    def get_profile_summary(self, name: str) -> dict
    """
    Return a lightweight summary for list display:
    { "name": str, "created_at": str, "updated_at": str, "roi_count": int }
    """
```

## Thread Safety

All public methods acquire `self._lock` (threading.Lock). I/O-bound methods
release the lock during actual file operations so reads/writes are serialized
but the UI thread is never blocked by file I/O.

## Error Handling

| Error | Raised When |
|---|---|
| `FileNotFoundError` | Profile file or index missing |
| `FileExistsError` | Save/rename target name already exists |
| `ValueError` | Corrupt JSON, schema validation failure |
| `OSError` | Disk full, permission denied, path too long |
