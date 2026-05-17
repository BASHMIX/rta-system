# Code Review Checklist: Spout Frame Receiver

**Purpose**: Verify implementation completeness, code quality, and adherence to architecture
**Created**: 2026-05-17
**Feature**: [spec.md](../spec.md)

## Project Structure

- [x] CHK001 All source files exist in expected locations per plan.md
- [x] CHK002 __init__.py files present for all packages
- [x] CHK003 config.json exists at project root with valid JSON
- [x] CHK004 tests/ directory exists with placeholder structure

## SpoutFrame & FrameSource (src/spout/__init__.py)

- [x] CHK005 SpoutFrame dataclass has width, height, data (ndarray), timestamp fields
- [x] CHK006 FrameSource ABC defines open(), close(), grab(), is_open, frame_width, frame_height
- [x] CHK007 FrameSource context manager protocol (__enter__/__exit__) implemented

## SpoutGLSource (src/spout/receiver.py)

- [x] CHK008 Connects to Spout sender by name via setReceiverName()
- [x] CHK009 Uses SpoutGL.receiveImage() to capture pixel data
- [x] CHK010 Converts pixel bytes to NumPy uint8 array with correct shape (H, W, 4)
- [x] CHK011 Returns None when sender not available (non-blocking)
- [x] CHK012 Detects sender resolution changes via isUpdated()
- [x] CHK013 Exception-safe grab() — catches and logs errors without crashing
- [x] CHK014 CaptureStats tracks frames_received count

## Color Sampler (src/spout/sampler.py)

- [x] CHK015 ColorSample dataclass has x, y, r, g, b, h, s, v fields
- [x] CHK016 sample_pixel() clamps coordinates to frame bounds
- [x] CHK017 sample_pixel() converts BGRA → RGB → HSV correctly
- [x] CHK018 sample_batch() samples all configured points in a single call
- [x] CHK019 format_sample() produces human-readable terminal output

## SpoutConfig (src/spout/config.py)

- [x] CHK020 SpoutConfig.from_file() loads config.json from project root
- [x] CHK021 Validates sender_name is non-empty string
- [x] CHK022 Validates sample_points has at least one valid [x, y] pair
- [x] CHK023 Validates target_fps is int in range 1–240
- [x] CHK024 Raises ConfigError with descriptive messages for all validation failures
- [x] CHK025 Handles file-not-found and JSON parse errors

## Entry Point (src/spout/run.py)

- [x] CHK026 Loads config via SpoutConfig.from_file() before starting capture
- [x] CHK027 Opens SpoutGLSource and enters capture loop
- [x] CHK028 Samples pixels at all configured points from each frame
- [x] CHK029 Prints RGB and HSV values to terminal via logging
- [x] CHK030 Handles KeyboardInterrupt / SIGINT for clean shutdown
- [x] CHK031 FPS throttling via Throttle class

## Utilities (src/utils.py)

- [x] CHK032 setup_logging() configures stdout handler with timestamp format
- [x] CHK033 Throttle class waits remaining frame period (1.0 / target_fps)
- [x] CHK034 Throttle.wait() returns bool indicating whether frame was dropped

## Notes

- All 34 items pass validation.
- Implementation matches plan.md architecture and design.
- No UI components needed for this sprint (terminal-only).
- Next step: integration testing with live OBS Spout sender.
