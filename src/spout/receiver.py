from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np

from src.spout import FrameSource, SpoutFrame

logger = logging.getLogger(__name__)


@dataclass
class CaptureStats:
    frames_received: int = 0
    frames_dropped: int = 0
    last_fps: float = 0.0


class SpoutGLSource(FrameSource):
    def __init__(self, sender_name: str):
        self._sender_name = sender_name
        self._receiver: Optional["SpoutGL.SpoutReceiver"] = None
        self._width = 0
        self._height = 0
        self._stats = CaptureStats()

    def open(self) -> None:
        import SpoutGL

        self._receiver = SpoutGL.SpoutReceiver()
        self._receiver.setReceiverName(self._sender_name)
        self._width = 0
        self._height = 0
        logger.info("Spout receiver opened for sender '%s'", self._sender_name)

    def close(self) -> None:
        if self._receiver is not None:
            self._receiver = None
            logger.info("Spout receiver closed")

    def grab(self) -> Optional[SpoutFrame]:
        if self._receiver is None:
            return None
        try:
            sender_name = self._sender_name
            w = self._receiver.getSenderWidth()
            h = self._receiver.getSenderHeight()
            if w == 0 or h == 0:
                return None
            if self._receiver.isUpdated():
                self._width = w
                self._height = h
            gl_format = (
                0x80E1  # GL_BGRA_EXT
            )
            pixels = self._receiver.receiveImage(
                sender_name, self._width, self._height, gl_format
            )
            if pixels is None or len(pixels) == 0:
                return None
            frame_data = np.frombuffer(pixels, dtype=np.uint8).reshape(
                (self._height, self._width, 4)
            )
            self._stats.frames_received += 1
            return SpoutFrame(
                width=self._width,
                height=self._height,
                data=frame_data,
                timestamp=time.perf_counter(),
            )
        except Exception:
            logger.warning("Failed to grab frame from Spout sender", exc_info=True)
            return None

    @property
    def is_open(self) -> bool:
        return self._receiver is not None

    @property
    def frame_width(self) -> int:
        return self._width

    @property
    def frame_height(self) -> int:
        return self._height

    @property
    def stats(self) -> CaptureStats:
        return self._stats
