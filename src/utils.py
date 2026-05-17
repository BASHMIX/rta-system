from __future__ import annotations

import logging
import time


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )


class Throttle:
    def __init__(self, target_fps: float):
        self._period = 1.0 / target_fps if target_fps > 0 else 0.0
        self._last = 0.0

    def wait(self) -> bool:
        now = time.perf_counter()
        elapsed = now - self._last
        if elapsed < self._period:
            time.sleep(self._period - elapsed)
            self._last = time.perf_counter()
            return False
        self._last = now
        return True
