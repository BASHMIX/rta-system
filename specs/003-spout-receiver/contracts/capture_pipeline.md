# Contract: Capture Pipeline Interface

**Date**: 2026-05-17 | **Branch**: `003-spout-receiver`

## FrameSource (Abstract Interface)

The internal abstraction used for dependency injection, enabling unit tests without a GPU.

```python
class FrameSource(ABC):
    """Abstract source of video frames."""

    @abstractmethod
    def open(self) -> None:
        """Initialize the frame source. May raise RuntimeError."""

    @abstractmethod
    def close(self) -> None:
        """Release the frame source."""

    @abstractmethod
    def grab(self) -> SpoutFrame | None:
        """Capture the latest frame. Returns None if nothing ready."""

    @property
    @abstractmethod
    def is_open(self) -> bool:
        """True if the source is initialized."""

    @property
    @abstractmethod
    def frame_width(self) -> int:
        """Current frame width."""

    @property
    @abstractmethod
    def frame_height(self) -> int:
        """Current frame height."""
```

## Implementations

### SpoutGLSource

Wraps the real `SpoutGL.SpoutReceiver` behind `FrameSource`. Connects to a Spout sender by name, receives frames as BGRA pixel data via `receiveImage`.

**Behavioral contract**:
- `open()` calls `SpoutGL.SpoutReceiver()` context manager internally and `setReceiverName(name)`
- `grab()` calls `receiveImage()` on the Spout receiver, wraps result in `SpoutFrame`
- `close()` releases the SpoutGL receiver
- If sender is not broadcasting, `grab()` returns `None` (not an error)
- On sender resolution change, `frame_width` / `frame_height` update automatically on next `grab()`

### MockFrameSource

Synthetic frame source for testing. Wraps a pre-generated NumPy array as a static frame.

**Behavioral contract**:
- `open()` is a no-op
- `grab()` returns a `SpoutFrame` with the pre-set synthetic data
- `close()` is a no-op
- `frame_width` / `frame_height` return the synthetic frame dimensions

## Capture Loop Contract

The capture loop in `main.py` follows this sequence:

```text
load_config()          → CaptureConfig
create FrameSource     → SpoutGLSource(config.sender_name)
open FrameSource
while running:
    frame = source.grab()
    if frame is None:
        sleep(0.01)    # backoff when no sender
        continue
    for (x, y) in config.sample_points:
        sample = sample_pixel(frame, x, y)
        print_sample(sample)
    throttle(target_fps)  # sleep remainder of frame period
close FrameSource
```

**Guarantees**:
- Frame drops when processing exceeds the frame period
- No unbounded queuing — only the most recent frame is kept
- `grab()` is non-blocking: returns `None` if no new frame from sender
- Reconnection is implicit: if sender reappears, `grab()` returns frames again
