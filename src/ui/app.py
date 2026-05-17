from __future__ import annotations

import json
import logging
import queue
import time
from pathlib import Path
from typing import Optional

import customtkinter as ctk
from PIL import Image

from src.obs.client import OBSClient
from src.roi import ROI
from src.roi.health_bar import HealthBarAnalyzer
from src.roi.text_ocr import TextAnalyzer
from src.roi.timer import TimerAnalyzer
from src.spout.receiver import SpoutGLSource
from src.ui.capture_thread import CaptureThread
from src.ui.tools_panel import ToolsPanel
from src.ui.workspace import Workspace
from src.ui.properties import PropertiesPanel
from src.utils import setup_logging

setup_logging()

logger = logging.getLogger(__name__)

CAPTURE_INTERVAL_MS = 33
CONFIG_PATH = Path("config.json")

ANALYZERS = {
    "health_bar": HealthBarAnalyzer(),
    "timer": TimerAnalyzer(),
    "text": TextAnalyzer(),
}


class RTAWorkspace(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RTA System")
        self.geometry("1280x720")
        self.minsize(1024, 600)

        self._spout_source = SpoutGLSource()
        self._obs_client = OBSClient()
        self._result_queue: queue.Queue = queue.Queue(maxsize=10)
        self._capture_thread: Optional[CaptureThread] = None
        self._mode = "setup"
        self._frame_skip = 2
        self._rois: list[ROI] = []
        self._selected_roi_id: Optional[str] = None

        self.grid_columnconfigure(0, weight=0, minsize=180)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0, minsize=280)
        self.grid_rowconfigure(0, weight=1)

        self.tools = ToolsPanel(
            self,
            on_tool_change=self._on_tool_change,
            on_upload=self._on_upload,
            on_mode_toggle=self._on_mode_toggle,
            on_frame_skip=self._on_frame_skip,
        )
        self.tools.grid(row=0, column=0, sticky="nsew", padx=(6, 3), pady=6)

        self.workspace = Workspace(
            self,
            obs_connect_cb=self._on_obs_connect,
            spout_select_cb=self._on_spout_select,
            on_roi_delete=self._on_roi_delete,
            on_roi_select=self._on_roi_select,
        )
        self.workspace.grid(row=0, column=1, sticky="nsew", padx=3, pady=6)

        self.properties = PropertiesPanel(
            self,
            on_add_roi=self._on_add_roi,
            on_mirror=self._on_mirror,
            on_save=self._on_save,
        )
        self.properties.grid(row=0, column=2, sticky="nsew", padx=(3, 6), pady=6)

        self.workspace.canvas.set_coords_callback(self._on_coords_change)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._open_spout()
        self._start_capture_thread()
        self.after(CAPTURE_INTERVAL_MS, self._process_results)
        self.after(1000, self._discover_spout_senders)
        self.after(2000, self._obs_poll_sources)

    def _open_spout(self) -> None:
        try:
            self._spout_source.open()
            logger.info("Spout receiver opened")
        except Exception as e:
            logger.error("Failed to open Spout: %s", e)

    def _start_capture_thread(self) -> None:
        self._capture_thread = CaptureThread(
            spout_source=self._spout_source,
            analyzers=ANALYZERS,
            result_queue=self._result_queue,
            interval_ms=CAPTURE_INTERVAL_MS,
        )
        self._capture_thread.set_mode(self._mode)
        self._capture_thread.set_frame_skip(self._frame_skip)
        self._capture_thread.start()

    def _process_results(self) -> None:
        while not self._result_queue.empty():
            try:
                data = self._result_queue.get_nowait()
                if data["type"] == "frame":
                    pil_img = Image.fromarray(data["rgb"])
                    self.workspace.canvas._render()
                elif data["type"] == "fps":
                    logger.debug("Capture FPS: %.1f", data["fps"])
                elif data["type"] == "analysis":
                    for result in data["results"]:
                        logger.info("ROI '%s' = %s", result.roi_name, result.value)
            except queue.Empty:
                break

        self.after(CAPTURE_INTERVAL_MS, self._process_results)

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

    def _obs_poll_sources(self) -> None:
        if self._obs_client.is_connected:
            sources = self._obs_client.get_inputs()
            logger.debug("OBS sources: %s", sources)
        self.after(5000, self._obs_poll_sources)

    def _on_upload(self, path: str) -> None:
        logger.info("Screenshot loaded: %s", path)
        self.workspace.canvas.load_screenshot(path)

    def _on_tool_change(self, tool: str) -> None:
        logger.info("Tool selected: %s", tool)

    def _on_mode_toggle(self, mode: str) -> None:
        self._mode = mode
        self.workspace.canvas.set_mode(mode)
        if self._capture_thread:
            self._capture_thread.set_mode(mode)
        logger.info("Mode switched to: %s", mode)

    def _on_frame_skip(self, val: int) -> None:
        self._frame_skip = val
        if self._capture_thread:
            self._capture_thread.set_frame_skip(val)
        logger.info("Frame skip set to: %d", val)

    def _on_coords_change(self, x: int, y: int, w: int, h: int) -> None:
        self.properties.update_coords(x, y, w, h)

    def _on_roi_delete(self, roi_id: str) -> None:
        self._rois = [r for r in self._rois if r.id != roi_id]
        self.workspace.canvas.remove_roi(roi_id)
        self.workspace.roi_list.remove_roi(roi_id)
        if self._capture_thread:
            self._capture_thread.remove_roi(roi_id)
        if self._selected_roi_id == roi_id:
            self._selected_roi_id = None
            self.properties.set_selected_roi(None)

    def _on_roi_select(self, roi_id: str) -> None:
        self._selected_roi_id = roi_id
        roi = next((r for r in self._rois if r.id == roi_id), None)
        self.properties.set_selected_roi(roi)

    def _on_add_roi(self, roi: ROI) -> None:
        tool_type = self.tools.get_tool_type()
        roi.tool_type = tool_type
        self._rois.append(roi)
        self.workspace.canvas.add_roi(roi)
        self.workspace.roi_list.add_roi(roi)
        if self._capture_thread:
            self._capture_thread.add_roi(roi)
        logger.info("ROI added: %s (%s)", roi.name, roi.tool_type)

    def _on_mirror(self, source_roi: ROI) -> None:
        mirrored = source_roi.mirror(screen_width=1920)
        self._rois.append(mirrored)
        self.workspace.canvas.add_roi(mirrored)
        self.workspace.roi_list.add_roi(mirrored)
        if self._capture_thread:
            self._capture_thread.add_roi(mirrored)
        logger.info("ROI mirrored: %s -> %s", source_roi.name, mirrored.name)

    def _on_save(self) -> None:
        config = {
            "spout": {
                "sender_name": self._spout_source._sender_name or "",
                "target_fps": 30,
            },
            "obs": {
                "host": self.workspace.obs_row.get_value(),
                "port": int(self.workspace.port_entry.get() or "4455"),
            },
            "rois": [r.to_dict() for r in self._rois],
            "frame_skip": self._frame_skip,
        }
        CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")
        logger.info("Config saved to %s", CONFIG_PATH.resolve())

    def _on_close(self) -> None:
        logger.info("Shutting down...")
        if self._capture_thread:
            self._capture_thread.stop()
            self._capture_thread.join(timeout=5.0)
        self._obs_client.disconnect()
        self.destroy()


def main():
    app = RTAWorkspace()
    app.mainloop()


if __name__ == "__main__":
    main()
