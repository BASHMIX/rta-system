# Research: Spout Frame Receiver

**Date**: 2026-05-17 | **Branch**: `003-spout-receiver`

## Methodology

Web search and code review of Spout Python bindings, existing receiver examples, and testing strategies.

## Unknowns Resolved

### 1. Which Spout Python package?

**Decision**: Use `SpoutGL` (`pip install SpoutGL`).

**Rationale**:
- Actively maintained — latest release v0.1.1 (March 2025) on PyPI
- Python 3.8+ support via pybind11 (covers our 3.10+ requirement)
- Exposes the full SpoutGL API including `receiveImage` / `sendImage`, `setFrameSync` / `waitFrameSync`, and data sharing
- Pure pip install — no Boost compilation or Visual Studio build step needed
- No external Python dependencies (OpenGL interop handled internally)
- Ships with examples for texture send/receive

**Alternatives considered**:
| Package | Status | Problem |
|---------|--------|---------|
| `spiraltechnica/Spout-for-Python` | Unmaintained | Requires Boost.Python, Python 3.5 only, manual .pyd build |
| `Off-World-Live/pyspout` | Sender only | No receiver support, requires VS build |
| `UnveilStudio/spout2-python` | Unknown maturity | Minimal docs, less community adoption |

### 2. How to test Spout receiver without a real GPU sender?

**Decision**: Use dependency injection with a `FrameSource` abstract base class. Unit tests inject synthetic NumPy frames; integration tests optionally use a real Spout sender.

**Rationale**:
- The receiver module wraps SpoutGL behind an ABC (`FrameSource`). Tests use a `MockFrameSource` that yields pre-defined NumPy arrays.
- The sampler and color conversion logic is tested independently with `numpy` fixtures — no Spout hardware needed.
- For end-to-end validation, the developer runs with OBS Spout output active.

**Testing Pyramid**:
| Layer | Scope | Spout required? |
|-------|-------|----------------|
| **Unit** | Sampler, color conversion, config parsing | No (synthetic NumPy) |
| **Integration** | Receiver connects to MockFrameSource | No |
| **E2E** | Full pipeline with OBS | Yes (manual/local) |

### 3. NumPy frame format from Spout

**Decision**: SpoutGL's `receiveImage` returns BGRA pixel bytes. Convert to NumPy uint8 array of shape `(height, width, 4)`, then convert to RGB using `cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)` and to HSV using `cv2.COLOR_RGB2HSV`.

**Data flow**:
```
SpoutGL.receiveImage() → bytes
  → np.frombuffer(bytes, dtype=np.uint8).reshape((h, w, 4))  # BGRA
  → cv2.cvtColor(bgra, cv2.COLOR_BGRA2RGB)                    # RGB
  → cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)                      # HSV
```

### 4. Sampling rate mechanism

**Decision**: Timer-based throttling using `time.perf_counter()`. After each frame receive + sample, calculate elapsed vs target period (`1.0 / target_fps`). If ahead, `time.sleep()` the remainder. If behind, skip that cycle (frame drop).

**Rationale**: Simple, deterministic, avoids unbounded queuing. Frame drops are natural when system can't keep up. No separate timer thread needed for this sprint.

### 5. Logging framework

**Decision**: Use Python `logging` module with a `StreamHandler` to stdout (terminal). Format: `[timestamp] [LEVEL] message`. Color values printed at `INFO` level.

**Rationale**: Structured, configurable, standard library. The constitution doesn't mandate a specific logger.

### 6. Config file location

**Decision**: Read from `config.json` in the project root. Spout config lives under a `"spout"` key matching existing `config.json` pattern from the constitution.

**Example `config.json`**:
```json
{
  "spout": {
    "sender_name": "OBS",
    "sample_points": [[100, 50], [200, 150]],
    "target_fps": 30
  }
}
```

## Key API Reference

### SpoutGL Receiver API

```python
import SpoutGL

# Context manager handles create/release
with SpoutGL.SpoutReceiver() as receiver:
    receiver.setReceiverName("SenderName")

    # Method A: Receive as OpenGL texture (requires GL context)
    receiver.receiveTexture(tex_id, GL_TEXTURE_2D, False, 0)

    # Method B: Receive as pixel bytes (no GL context needed)
    pixels = receiver.receiveImage(sender_name, width, height, gl_format)

    # Query sender info
    w = receiver.getSenderWidth()
    h = receiver.getSenderHeight()
    if receiver.isUpdated():
        # handle resolution change
        pass
```

### OpenCV Color Conversion

```python
import cv2
import numpy as np

# Convert BGRA → RGB
rgb = cv2.cvtColor(bgra_frame, cv2.COLOR_BGRA2RGB)

# Convert RGB → HSV
hsv = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2HSV)

# Sample single pixel
pixel_rgb = rgb_frame[y, x]  # returns [r, g, b]
pixel_hsv = hsv_frame[y, x]  # returns [h, s, v]
```
