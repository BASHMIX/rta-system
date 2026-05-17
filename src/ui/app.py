from __future__ import annotations

import logging
import time

import customtkinter as ctk
from PIL import Image

from src.obs.client import OBSClient
from src.spout.receiver import SpoutGLSource
from src.ui.tools_panel import ToolsPanel
from src.ui.workspace import Workspace
from src.ui.properties import PropertiesPanel
from src.utils import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

CAPTURE_INTERVAL_MS = 33


class RTAWorkspace(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RTA System")
        self.geometry("1280x720")
        self.minsize(1024, 600)

        self._spout_source = SpoutGLSource()
        self._obs_client = OBSClient()
        self._frame_count = 0
        self._fps_timer = time.perf_counter()

        self.grid_columnconfigure(0, weight=0, minsize=180)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0, minsize=280)
        self.grid_rowconfigure(0, weight=1)

        self.tools = ToolsPanel(self, on_tool_change=self._on_tool_change)
        self.tools.grid(row=0, column=0, sticky="nsew", padx=(6, 3), pady=6)

        self.workspace = Workspace(
            self,
            obs_connect_cb=self._on_obs_connect,
            spout_select_cb=self._on_spout_select,
        )
        self.workspace.grid(row=0, column=1, sticky="nsew", padx=3, pady=6)

        self.properties = PropertiesPanel(self)
        self.properties.grid(row=0, column=2, sticky="nsew", padx=(3, 6), pady=6)

        self._open_spout()
        self.after(1000, self._discover_spout_senders)
        self.after(CAPTURE_INTERVAL_MS, self._capture_loop)

    def _open_spout(self) -> None:
        try:
            self._spout_source.open()
            logger.info("Spout receiver opened")
        except Exception as e:
            logger.error("Failed to open Spout: %s", e)

    def _discover_spout_senders(self) -> None:
        senders = self._spout_source.get_available_senders()
        self.workspace.refresh_spout_list(senders)
        self.after(3000, self._discover_spout_senders)

    def _on_spout_select(self, sender_name: str) -> None:
        logger.info("Spout sender selected: %s", sender_name)
        self._spout_source.set_sender(sender_name)
        self.workspace.set_spout_connected(True)

    def _on_obs_connect(self, connect: bool) -> bool:
        if connect:
            host = self.workspace.obs_row.get_value()
            port_str = self.workspace.port_entry.get().strip()
            port = int(port_str) if port_str.isdigit() else 4455
            ok = self._obs_client.connect(host, port)
            if ok:
                logger.info("OBS connected to %s:%d", host, port)
            else:
                logger.error("OBS connection failed to %s:%d", host, port)
            return ok
        else:
            self._obs_client.disconnect()
            logger.info("OBS disconnected")
            return True

    def _capture_loop(self) -> None:
        frame = self._spout_source.grab()
        if frame is not None:
            self._frame_count += 1
            rgb_data = frame.data[:, :, [2, 1, 0]]
            pil_img = Image.fromarray(rgb_data)
            self.workspace.set_canvas_image(pil_img)
            now = time.perf_counter()
            elapsed = now - self._fps_timer
            if elapsed >= 2.0:
                fps = self._frame_count / elapsed
                logger.debug("Capture FPS: %.1f", fps)
                self._update_json(fps)
                self._frame_count = 0
                self._fps_timer = now
        self.after(CAPTURE_INTERVAL_MS, self._capture_loop)

    def _update_json(self, fps: float = 0.0) -> None:
        data = {
            "spout": {
                "sender": self._spout_source._sender_name,
                "resolution": (
                    f"{self._spout_source.frame_width}x{self._spout_source.frame_height}"
                    if self._spout_source.frame_width > 0
                    else "N/A"
                ),
                "status": "connected" if self._spout_source.is_open else "disconnected",
                "fps": round(fps, 1),
            }
        }
        self.workspace.update_json(data)

    def _on_tool_change(self, tool: str) -> None:
        logger.info("Tool selected: %s", tool)
