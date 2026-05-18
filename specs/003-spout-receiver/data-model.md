# Data Model: Phase 2 — UX Refinements

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
    obs_target: OBSTarget      # NEW: hierarchical target
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

## ScaleMode (New)

```python
SCALE_MODES = {
    "native": (None, None),    # Use sender resolution
    "1080p": (1920, 1080),
    "720p": (1280, 720),
}
```

## Canvas State (New)

```python
@dataclass
class CanvasState:
    scale_mode: str            # "native" | "1080p" | "720p"
    selected_roi_id: str | None
    is_drawing: bool           # True when creating new ROI
    is_moving: bool            # True when dragging selected ROI
    is_resizing: bool          # True when dragging resize handle
    resize_handle: str | None  # "tl" | "tr" | "bl" | "br" | "t" | "b" | "l" | "r"
    drag_offset: tuple[int, int]  # (dx, dy) for move operations
```

## Validation Rules

- ROI width/height must be >= 10 pixels (minimum viable sampling area)
- ROI coordinates must be within screen bounds (clamped on save)
- OBSTarget type="filter" requires non-empty `source` field
- Scale mode changes must preserve ROI coordinate proportions

## State Transitions

### ROI Interaction State Machine

```
IDLE → DRAWING (click on empty canvas)
IDLE → SELECTED (click inside existing ROI)
SELECTED → MOVING (drag inside ROI)
SELECTED → RESIZING (drag on edge/corner handle)
SELECTED → IDLE (click outside ROI)
DRAWING → IDLE (mouse release)
MOVING → SELECTED (mouse release)
RESIZING → SELECTED (mouse release)
```
