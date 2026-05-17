from __future__ import annotations

import array
import logging
import time
from dataclasses import dataclass
from itertools import repeat
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
    def __init__(self, sender_name: str = ""):
        self._sender_name = sender_name
        self._receiver: Optional["SpoutGL.SpoutReceiver"] = None
        self._width = 0
        self._height = 0
        self._stats = CaptureStats()
        self._buffer: Optional[array.array] = None

    def open(self) -> None:
        import SpoutGL

        self._receiver = SpoutGL.SpoutReceiver()
        if self._sender_name:
            self._receiver.setReceiverName(self._sender_name)
        self._width = 0
        self._height = 0
        self._buffer = None
        logger.info("Spout receiver opened for sender '%s'", self._sender_name)

    def close(self) -> None:
        if self._receiver is not None:
            try:
                self._receiver.releaseReceiver()
            except Exception:
                pass
            self._receiver = None
            self._buffer = None
            logger.info("Spout receiver closed")

    def set_sender(self, name: str) -> None:
        self.close()
        self._sender_name = name
        self.open()
        logger.info("Spout receiver switched to sender '%s'", name)

    def grab(self) -> Optional[SpoutFrame]:
        if self._receiver is None:
            return None
        try:
            import SpoutGL

            result = self._receiver.receiveImage(
                self._buffer, SpoutGL.enums.GL_BGRA_EXT, False, 0
            )

            if self._receiver.isUpdated():
                self._width = self._receiver.getSenderWidth()
                self._height = self._receiver.getSenderHeight()
                logger.info("Sender resolution: %dx%d", self._width, self._height)
                buf_size = self._width * self._height * 4
                self._buffer = array.array("B", repeat(0, buf_size))

            if self._buffer is None or self._width == 0 or self._height == 0:
                return None

            if not result:
                return None

            if SpoutGL.helpers.isBufferEmpty(self._buffer):
                return None

            frame_data = np.frombuffer(self._buffer, dtype=np.uint8).reshape(
                (self._height, self._width, 4)
            )
            self._stats.frames_received += 1

            self._receiver.waitFrameSync(self._sender_name, 1)

            return SpoutFrame(
                width=self._width,
                height=self._height,
                data=frame_data.copy(),
                timestamp=time.perf_counter(),
            )
        except Exception:
            logger.warning("Failed to grab frame from Spout sender", exc_info=True)
            return None

    def get_available_senders(self) -> list[str]:
        if self._receiver is None:
            return []
        try:
            return self._receiver.getSenderList()
        except Exception:
            logger.warning("Failed to list Spout senders", exc_info=True)
            return []

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
