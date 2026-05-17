# Integration Checklist: Spout Frame Receiver

**Purpose**: Verify end-to-end functionality with real Spout sender (OBS Studio)
**Created**: 2026-05-17
**Feature**: [spec.md](../spec.md)

## Prerequisites

- [ ] INT001 OBS Studio installed with Spout 2 output plugin
- [ ] INT002 Spout 2 SDK installed ([download](https://leadedge.github.io/))
- [ ] INT003 Python dependencies installed: `pip install numpy opencv-python SpoutGL`
- [ ] INT004 Python 3.10+ virtual environment active
- [ ] INT005 DirectX 11 compatible GPU with up-to-date drivers

## OBS Spout Output Setup

- [ ] INT006 OBS Spout output configured with a known sender name (e.g., "OBS")
- [ ] INT007 OBS is sending a video source (game capture, test pattern, or color source)
- [ ] INT008 OBS is actively broadcasting (Spout sender visible in SpoutSettings)

## Configuration

- [ ] INT009 config.json `spout.sender_name` matches the OBS Spout sender name
- [ ] INT010 config.json `spout.sample_points` contains valid coordinates within OBS output resolution
- [ ] INT011 config.json `spout.target_fps` set to 30

## Execution

- [ ] INT012 Run `python src/spout/run.py` from project root
- [ ] INT013 Terminal shows `[INFO] Spout receiver opened for sender 'OBS'` without errors
- [ ] INT014 Terminal shows `[INFO] Frame WxH @ FPS` within 2 seconds
- [ ] INT015 Terminal shows `[INFO]   (x, y): RGB(r, g, b) HSV(h, s, v)` lines for all sample points
- [ ] INT016 RGB and HSV values change when OBS output content changes
- [ ] INT017 Frame rate is approximately at configured target_fps (within ±10%)

## Disconnection & Reconnection

- [ ] INT018 Stop OBS Spout output — terminal logs disconnection without crash
- [ ] INT019 Restart OBS Spout output — capture resumes within 2 seconds
- [ ] INT020 Fast repeated stop/start cycles don't cause errors or memory leaks

## Resolution Change

- [ ] INT021 Change OBS output resolution — terminal logs `Resolution changed: WxH`
- [ ] INT022 Sampling continues at new resolution without errors

## Error Handling

- [ ] INT023 Delete config.json — run.py exits with descriptive ConfigError
- [ ] INT024 Set invalid sender name — run.py logs failure and exits cleanly
- [ ] INT025 Set empty sample_points — run.py exits with validation error
- [ ] INT026 Set target_fps to 0 — run.py exits with validation error

## Notes

- Mark items as `[x]` when verified.
- Integration testing requires a Windows machine with OBS Studio installed.
- OBS must be running with Spout output active before launching the receiver.
