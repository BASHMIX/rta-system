# Quickstart: Spout Frame Receiver

**Branch**: `003-spout-receiver`

## Prerequisites

- Windows 10/11 with DirectX 11 compatible GPU
- Python 3.10+
- OBS Studio (or any Spout sender) with Spout output plugin
- Spout 2 SDK installed ([download](https://leadedge.github.io/))

## Setup

```powershell
# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install numpy opencv-python SpoutGL
```

## Configuration

Create `config.json` in the project root:

```json
{
  "spout": {
    "sender_name": "OBS",
    "sample_points": [[640, 360], [200, 150]],
    "target_fps": 30
  }
}
```

## Run

```powershell
# Ensure OBS is running with Spout output active
python src/main.py
```

## Expected Output

Terminal displays sampled pixel colors like:

```
[12:34:56] Frame 1920x1080 @ 30.0 FPS
[12:34:56]   (640, 360): RGB(42, 180, 220) HSV(112, 80, 220)
[12:34:56]   (200, 150): RGB(10, 10, 10) HSV(0, 0, 10)
[12:34:57] Frame 1920x1080 @ 30.0 FPS
...
```

## Testing

```powershell
pytest tests/
```

Unit tests run without Spout hardware — they use synthetic NumPy frames.

## Project Layout (relevant files)

```
src/
├── spout/
│   ├── __init__.py
│   ├── receiver.py      # SpoutGLSource (FrameSource impl)
│   ├── sampler.py       # ColorSampler: coordinate clamping, RGB→HSV
│   └── config.py        # SpoutConfig: load/parse/validate config
├── main.py              # Entry point — capture loop
└── utils.py             # Color conversions, throttle timer, logging setup

tests/
├── test_receiver.py     # MockFrameSource tests
├── test_sampler.py      # Sampling + conversion tests
└── test_config.py       # Config validation tests
```

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `ImportError: No module named SpoutGL` | SpoutGL not installed | `pip install SpoutGL` |
| `grab()` returns None continuously | No Spout sender active | Start OBS with Spout output |
| `RuntimeError: No Spout senders found` | Sender name mismatch | Check sender name in OBS vs config.json |
| Low FPS (< target) | GPU/system can't keep up | Lower `target_fps`, reduce sample_points |
