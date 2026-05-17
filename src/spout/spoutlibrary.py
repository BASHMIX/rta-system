from __future__ import annotations

import ctypes
import ctypes.wintypes
import logging
import os
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np

from src.spout import FrameSource, SpoutFrame

logger = logging.getLogger(__name__)

GL_RGBA = 0x1908
GL_BGRA_EXT = 0x80E1


class SpoutLibrarySource(FrameSource):
    """Spout receiver using SpoutLibrary.dll (Spout2 SDK C API) via ctypes."""

    def __init__(self, sender_name: str = ""):
        self._sender_name = sender_name
        self._width = 0
        self._height = 0
        self._buffer: Optional[bytearray] = None
        self._handle: Optional[int] = None  # SPOUTHANDLE pointer
        self._vtable: Optional[int] = None  # vtable pointer
        self._dll_dir = os.path.dirname(os.path.abspath(__file__))
        self._dll_path = os.path.join(self._dll_dir, "SpoutLibrary.dll")

    def _load_dll(self) -> bool:
        if not os.path.exists(self._dll_path):
            logger.error("SpoutLibrary.dll not found at %s", self._dll_path)
            return False
        try:
            self._dll = ctypes.WinDLL(self._dll_path)
            get_spout = self._dll.GetSpout
            get_spout.restype = ctypes.c_void_p
            get_spout.argtypes = []
            self._handle = get_spout()
            if not self._handle:
                logger.error("GetSpout() returned NULL")
                return False
            self._vtable = ctypes.c_void_p.from_address(self._handle).value
            logger.info("SpoutLibrary.dll loaded, handle=%#x", self._handle)
            return True
        except Exception as e:
            logger.error("Failed to load SpoutLibrary.dll: %s", e)
            return False

    def _call(self, index: int, restype, *args):
        """Call a vtable method by index."""
        vtable = ctypes.c_void_p(self._vtable).value
        func_ptr = ctypes.c_void_p.from_address(vtable + index * 8).value
        func_type = ctypes.WINFUNCTYPE(restype, ctypes.c_void_p, *[ctypes.c_void_p if isinstance(a, (int, type(None))) else type(a) for a in args])
        func = func_type(func_ptr)
        return func(self._handle, *args)

    def open(self) -> None:
        if not self._load_dll():
            return
        if self._sender_name:
            self._set_receiver_name(self._sender_name)
        logger.info("SpoutLibrary receiver opened for '%s'", self._sender_name)

    def close(self) -> None:
        if self._handle:
            try:
                self._release_receiver()
            except Exception:
                pass
            self._handle = None
            self._vtable = None
            self._buffer = None
            logger.info("SpoutLibrary receiver closed")

    def _set_receiver_name(self, name: str) -> None:
        # vtable index 15: SetReceiverName(const char*)
        func_ptr = ctypes.c_void_p.from_address(self._vtable + 15 * 8).value
        func = ctypes.WINFUNCTYPE(None, ctypes.c_void_p, ctypes.c_char_p)(func_ptr)
        func(self._handle, name.encode("utf-8"))

    def _release_receiver(self) -> None:
        # vtable index 17: ReleaseReceiver()
        func_ptr = ctypes.c_void_p.from_address(self._vtable + 17 * 8).value
        func = ctypes.WINFUNCTYPE(None, ctypes.c_void_p)(func_ptr)
        func(self._handle)

    def _receive_image(self, pixels, gl_format, invert, host_fbo) -> bool:
        # vtable index 19: ReceiveImage(unsigned char*, GLenum, bool, GLuint)
        func_ptr = ctypes.c_void_p.from_address(self._vtable + 19 * 8).value
        func = ctypes.WINFUNCTYPE(
            ctypes.c_bool,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_bool,
            ctypes.c_uint,
        )(func_ptr)
        return func(self._handle, pixels, gl_format, invert, host_fbo)

    def _is_updated(self) -> bool:
        # vtable index 20: IsUpdated()
        func_ptr = ctypes.c_void_p.from_address(self._vtable + 20 * 8).value
        func = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p)(func_ptr)
        return func(self._handle)

    def _get_sender_width(self) -> int:
        # vtable index 24: GetSenderWidth()
        func_ptr = ctypes.c_void_p.from_address(self._vtable + 24 * 8).value
        func = ctypes.WINFUNCTYPE(ctypes.c_uint, ctypes.c_void_p)(func_ptr)
        return func(self._handle)

    def _get_sender_height(self) -> int:
        # vtable index 25: GetSenderHeight()
        func_ptr = ctypes.c_void_p.from_address(self._vtable + 25 * 8).value
        func = ctypes.WINFUNCTYPE(ctypes.c_uint, ctypes.c_void_p)(func_ptr)
        return func(self._handle)

    def _get_sender_count(self) -> int:
        # vtable index 111: GetSenderCount()
        func_ptr = ctypes.c_void_p.from_address(self._vtable + 111 * 8).value
        func = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p)(func_ptr)
        return func(self._handle)

    def _get_sender(self, index: int) -> Optional[str]:
        # vtable index 112: GetSender(int, char*, int) -> bool
        func_ptr = ctypes.c_void_p.from_address(self._vtable + 112 * 8).value
        buf = ctypes.create_string_buffer(256)
        func = ctypes.WINFUNCTYPE(
            ctypes.c_bool, ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int
        )(func_ptr)
        if func(self._handle, index, buf, 256):
            return buf.value.decode("utf-8")
        return None

    def _wait_frame_sync(self, sender_name: str, timeout: int = 0) -> bool:
        # vtable index 43: WaitFrameSync(const char*, DWORD) -> bool
        func_ptr = ctypes.c_void_p.from_address(self._vtable + 43 * 8).value
        func = ctypes.WINFUNCTYPE(
            ctypes.c_bool, ctypes.c_void_p, ctypes.c_char_p, ctypes.wintypes.DWORD
        )(func_ptr)
        return func(self._handle, sender_name.encode("utf-8"), timeout)

    def set_sender(self, name: str) -> None:
        self.close()
        self._sender_name = name
        self.open()
        logger.info("SpoutLibrary receiver switched to '%s'", name)

    def grab(self) -> Optional[SpoutFrame]:
        if self._handle is None:
            return None
        try:
            result = self._receive_image(
                ctypes.cast(self._buffer, ctypes.c_void_p) if self._buffer else None,
                GL_RGBA,
                False,
                0,
            )

            if self._is_updated():
                self._width = self._get_sender_width()
                self._height = self._get_sender_height()
                logger.info(
                    "Sender '%s' resolution: %dx%d",
                    self._sender_name,
                    self._width,
                    self._height,
                )
                self._buffer = bytearray(self._width * self._height * 4)

            if self._buffer is None or self._width == 0 or self._height == 0:
                logger.debug("grab: no buffer or zero size")
                return None

            if not result:
                logger.debug("grab: ReceiveImage returned False")
                return None

            frame_data = np.frombuffer(self._buffer, dtype=np.uint8).reshape(
                (self._height, self._width, 4)
            )

            if not np.any(frame_data):
                logger.debug("grab: frame is all zeros")
                return None

            return SpoutFrame(
                width=self._width,
                height=self._height,
                data=frame_data.copy(),
                timestamp=time.perf_counter(),
            )
        except Exception:
            logger.warning("Failed to grab frame", exc_info=True)
            return None
        finally:
            try:
                self._wait_frame_sync(self._sender_name, 10000)
            except Exception:
                pass

    def get_available_senders(self) -> list[str]:
        if self._handle is None:
            return []
        try:
            count = self._get_sender_count()
            senders = []
            for i in range(count):
                name = self._get_sender(i)
                if name:
                    senders.append(name)
            return senders
        except Exception:
            logger.warning("Failed to list senders", exc_info=True)
            return []

    @property
    def is_open(self) -> bool:
        return self._handle is not None

    @property
    def frame_width(self) -> int:
        return self._width

    @property
    def frame_height(self) -> int:
        return self._height
