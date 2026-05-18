# Data Model: Phase 2 — UX Refinements & Canvas Polish

## ROI (Updated)

```python
@dataclass
class ROI:
    id: str                    # UUID short (8 chars)
    name: str                  # User-defined name
    x: int                     # Top-left X (screen coordinates)
    y: int                     # Top-left Y (screen coordinates)
    width: int                 # Width in pixels
    height: int                # Height in pixels
    tool_type: str             # "health_bar" | "timer" | "text"
    player: int                # 1 or 2
    obs_target: OBSTarget      # Hierarchical OBS target
    mirrored_from: str         # Source ROI name (empty if not mirrored)
```

## OBSTarget (New)

```python
@dataclass
class OBSTarget:
    type: str                  # "source" | "filter"
    name: str                  # Source name or filter name
    source: str                # Parent source name (only if type="filter")
    action: str                # "visibility_on" | "visibility_off" | "filter_enable" | "filter_disable"
```
