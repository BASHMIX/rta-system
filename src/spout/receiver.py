from __future__ import annotations

import ctypes
import logging
import os
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np

from src.spout import FrameSource, SpoutFrame

logger = logging.getLogger(__name__)

GL_TEXTURE_2D = 0x0DE1
GL_TEXTURE_MIN_FILTER = 0x2801
GL_TEXTURE_MAG_FILTER = 0x2800
GL_LINEAR = 0x2601
GL_RGBA = 0x1908
GL_UNSIGNED_BYTE = 0x1401

_gl = ctypes.windll.opengl32
_user32 = ctypes.windll.user32
_gdi32 = ctypes.windll.gdi32


class _GLContext:
    _instance = None
    _ref_count = 0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._handle = None
        self._vtable = None
        self._dll = None
        self._create()

    def _create(self):
        dll_path = r"D:\Desktop\OBS Automation System\src\spout\SpoutLibrary.dll"
        if not os.path.exists(dll_path):
            logger.error("SpoutLibrary.dll not found at %s", dll_path)
            return

        self._dll = ctypes.WinDLL(dll_path)
        get_spout = self._dll.GetSpout
        get_spout.restype = ctypes.c_void_p
        self._handle = get_spout()
        if not self._handle:
            logger.error("GetSpout() returned NULL")
            return
        self._vtable = ctypes.c_void_p.from_address(self._handle).value

        # Create OpenGL context via SpoutLibrary (handles GPU affinity)
        f_gl = self._vfunc(151, ctypes.c_bool, ctypes.c_void_p)
        result = f_gl(self._handle, None)
        if result:
            logger.debug("SpoutLibrary OpenGL context created")
        else:
            logger.error("SpoutLibrary CreateOpenGL failed")

    def _vfunc(self, idx, restype, *argtypes):
        func_ptr = ctypes.c_void_p.from_address(self._vtable + idx * 8).value
        return ctypes.WINFUNCTYPE(restype, ctypes.c_void_p, *argtypes)(func_ptr)

    def make_current(self):
        pass

    def release(self):
        _GLContext._ref_count -= 1
        if _GLContext._ref_count <= 0 and self._handle:
            f_close = self._vfunc(152, ctypes.c_bool)
            f_close(self._handle)
            f_rel = self._vfunc(171, None)
            f_rel(self._handle)
            self._handle = None
            self._vtable = None
            _GLContext._instance = None
            logger.debug("SpoutLibrary OpenGL context destroyed")

    @classmethod
    def acquire(cls):
        cls._ref_count += 1
        inst = cls()
        return inst

    @classmethod
    def release_all(cls):
        if cls._instance:
            cls._instance.release()
            cls._instance = None


@dataclass
class CaptureStats:
    frames_received: int = 0
    frames_dropped: int = 0
    last_fps: float = 0.0


class SpoutGLSource(FrameSource):
    def __init__(self, sender_name: str = ""):
        self._sender_name = sender_name
        self._receiver = None
        self._tex_id = 0
        self._width = 0
        self._height = 0
        self._stats = CaptureStats()
        self._gl_ctx = None

    def open(self) -> None:
        import SpoutGL

        self._receiver = SpoutGL.SpoutReceiver()
        if self._sender_name:
            self._receiver.setReceiverName(self._sender_name)

        self._gl_ctx = _GLContext.acquire()

        tex_id = ctypes.c_uint(0)
        _gl.glGenTextures(1, ctypes.byref(tex_id))
        self._tex_id = tex_id.value
        if self._tex_id == 0:
            logger.error("glGenTextures returned 0 — no valid OpenGL context")
        _gl.glBindTexture(GL_TEXTURE_2D, self._tex_id)
        _gl.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        _gl.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        self._width = 0
        self._height = 0
        logger.info("Spout receiver opened for sender '%s'", self._sender_name)

    def close(self) -> None:
        if self._receiver is not None:
            try:
                self._receiver.releaseReceiver()
            except Exception:
                pass
            self._receiver = None

        if self._tex_id:
            tex_id = ctypes.c_uint(self._tex_id)
            _gl.glDeleteTextures(1, ctypes.byref(tex_id))
            self._tex_id = 0

        if self._gl_ctx:
            self._gl_ctx.release()
            self._gl_ctx = None

        self._width = 0
        self._height = 0
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

            self._gl_ctx.make_current()

            result = self._receiver.receiveTexture(
                self._tex_id, GL_TEXTURE_2D, False, 0
            )

            if self._receiver.isUpdated():
                self._width = self._receiver.getSenderWidth()
                self._height = self._receiver.getSenderHeight()
                logger.info(
                    "Sender '%s' resolution: %dx%d",
                    self._sender_name,
                    self._width,
                    self._height,
                )
                _gl.glBindTexture(GL_TEXTURE_2D, self._tex_id)
                _gl.glTexImage2D(
                    GL_TEXTURE_2D, 0, GL_RGBA,
                    self._width, self._height, 0,
                    GL_RGBA, GL_UNSIGNED_BYTE, None,
                )

            if self._width == 0 or self._height == 0:
                logger.debug("grab: zero size %dx%d", self._width, self._height)
                return None

            if not result:
                logger.debug("grab: receiveTexture returned False")
                return None

            buf_size = self._width * self._height * 4
            buf = (ctypes.c_ubyte * buf_size)()
            _gl.glBindTexture(GL_TEXTURE_2D, self._tex_id)
            _gl.glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_BYTE, buf)

            frame_data = np.frombuffer(buf, dtype=np.uint8).reshape(
                (self._height, self._width, 4)
            )

            if not np.any(frame_data):
                logger.debug("grab: frame is all zeros")
                return None

            self._stats.frames_received += 1
            return SpoutFrame(
                width=self._width,
                height=self._height,
                data=frame_data.copy(),
                timestamp=time.perf_counter(),
            )
        except Exception:
            logger.warning("Failed to grab frame from Spout sender", exc_info=True)
            return None
        finally:
            try:
                self._receiver.waitFrameSync(self._sender_name, 10000)
            except Exception:
                pass

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
