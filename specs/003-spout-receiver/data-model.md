# Data Model: Spout Frame Receiver

**Date**: 2026-05-17 | **Branch**: `003-spout-receiver`

## Entities

### SpoutFrame

A single video frame received from the Spout sender.

| Field | Type | Description |
|-------|------|-------------|
| `width` | `int` | Frame width in pixels |
| `height` | `int` | Frame height in pixels |
| `data` | `np.ndarray` | Pixel data as BGRA uint8 array, shape `(H, W, 4)` |
| `timestamp` | `float` | `time.perf_counter()` value at capture time |

**Validation**:
- `width > 0` and `height > 0`
- `data.shape == (height, width, 4)`
- `data.dtype == np.uint8`

**State transitions**: N/A (immutable value object)

---

### SpoutReceiver

Manages the Spout connection lifecycle.

| Field | Type | Description |
|-------|------|-------------|
| `_receiver` | `SpoutGL.SpoutReceiver \| None` | Underlying SpoutGL receiver instance |
| `_sender_name` | `str` | Name of the Spout sender to connect to |
| `_width` | `int` | Most recent frame width |
| `_height` | `int` | Most recent frame height |
| `_connected` | `bool` | Whether currently connected to a sender |

**Methods**:
| Method | Returns | Description |
|--------|---------|-------------|
| `connect()` | `None` | Open Spout receiver and set sender name |
| `disconnect()` | `None` | Release Spout receiver |
| `receive_frame()` | `SpoutFrame \| None` | Capture latest frame, or None if not ready |
| `is_connected()` | `bool` | Check connection status |

**State transitions**:
```
disconnected → connect() → connected
connected → disconnect() → disconnected
connected → (sender lost) → disconnected → (auto-retry) → connected
```

**Validation**:
- `connect()` must be called before `receive_frame()`
- `receive_frame()` returns `None` if sender not active

---

### ColorSample

A single pixel color reading at a coordinate.

| Field | Type | Description |
|-------|------|-------------|
| `x` | `int` | X coordinate (column) |
| `y` | `int` | Y coordinate (row) |
| `r` | `int` | Red channel (0–255) |
| `g` | `int` | Green channel (0–255) |
| `b` | `int` | Blue channel (0–255) |
| `h` | `int` | Hue (0–179 in OpenCV HSV) |
| `s` | `int` | Saturation (0–255) |
| `v` | `int` | Value (0–255) |

**Validation**:
- `0 <= x < frame_width`
- `0 <= y < frame_height`
- `0 <= r,g,b <= 255`
- `0 <= h <= 179`, `0 <= s,v <= 255`

---

### CaptureConfig

Configuration for the capture pipeline.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sender_name` | `str` | `"OBS"` | Spout sender name to connect to |
| `sample_points` | `list[tuple[int,int]]` | `[(100, 100)]` | List of (x, y) pixel coordinates to sample |
| `target_fps` | `int` | `30` | Target frame processing rate |

**Validation**:
- `sender_name` must be non-empty string
- `sample_points` must have at least one point
- Each point: `x >= 0`, `y >= 0`
- `target_fps` must be in range `[1, 240]`

**Source**: Loaded from `config.json["spout"]` at startup.

## Relationships

```
CaptureConfig (1) ──configures──> SpoutReceiver (1)
SpoutReceiver (1) ──produces──> SpoutFrame (N)
SpoutFrame (1) ──sampled at──> ColorSample (N)
CaptureConfig (1) ──defines──> sample_points (N) ──used for──> ColorSample (N)
```
