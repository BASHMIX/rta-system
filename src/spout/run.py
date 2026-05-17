from __future__ import annotations

import logging
import signal
import sys
import time

from src.spout.config import ConfigError, SpoutConfig
from src.spout.receiver import SpoutGLSource
from src.spout.sampler import format_sample, sample_batch
from src.utils import Throttle, setup_logging

logger = logging.getLogger(__name__)

_RUNNING = True


def _signal_handler(sig, frame):
    global _RUNNING
    _RUNNING = False


def main():
    setup_logging()
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    try:
        config = SpoutConfig.from_file("config.json")
    except ConfigError as e:
        logger.error("Configuration error: %s", e)
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error("config.json not found: %s", e)
        sys.exit(1)

    source = SpoutGLSource(config.sender_name)
    throttle = Throttle(config.target_fps)
    prev_width = 0
    prev_height = 0
    frames_since_log = 0
    log_timer = time.perf_counter()

    logger.info(
        "Starting Spout capture: sender='%s', %d points, %d FPS",
        config.sender_name,
        len(config.sample_points),
        config.target_fps,
    )

    try:
        source.open()
    except Exception as e:
        logger.error("Failed to open Spout receiver: %s", e)
        sys.exit(1)

    logger.info("Connected. Waiting for frames from '%s'...", config.sender_name)

    while _RUNNING:
        frame = source.grab()

        if frame is None:
            time.sleep(0.01)
            continue

        frames_since_log += 1

        if prev_width != frame.width or prev_height != frame.height:
            logger.info("Resolution changed: %dx%d", frame.width, frame.height)
            prev_width = frame.width
            prev_height = frame.height

        samples = sample_batch(frame.data, config.sample_points)
        now = time.perf_counter()
        elapsed = now - log_timer
        if elapsed >= 1.0:
            fps = frames_since_log / elapsed if elapsed > 0 else 0.0
            logger.info(
                "Frame %dx%d @ %.1f FPS",
                frame.width,
                frame.height,
                fps,
            )
            for s in samples:
                logger.info("  %s", format_sample(s))
            frames_since_log = 0
            log_timer = now

        throttle.wait()

    source.close()
    logger.info("Spout capture stopped.")


if __name__ == "__main__":
    main()
