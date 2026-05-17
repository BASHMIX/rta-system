from __future__ import annotations

import json

import customtkinter as ctk

from src.spout.receiver import SpoutGLSource
from src.ui.tools_panel import ToolsPanel
from src.ui.workspace import Workspace
from src.ui.properties import PropertiesPanel
from src.utils import setup_logging

setup_logging()
import logging

logger = logging.getLogger(__name__)


class RTAWorkspace(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RTA System")
        self.geometry("1280x720")
        self.minsize(1024, 600)

        self._spout_source = SpoutGLSource()

        self.grid_columnconfigure(0, weight=0, minsize=180)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0, minsize=280)
        self.grid_rowconfigure(0, weight=1)

        self.tools = ToolsPanel(self, on_tool_change=self._on_tool_change)
        self.tools.grid(row=0, column=0, sticky="nsew", padx=(6, 3), pady=6)

        self.workspace = Workspace(self)
        self.workspace.grid(row=0, column=1, sticky="nsew", padx=3, pady=6)

        self.properties = PropertiesPanel(self)
        self.properties.grid(row=0, column=2, sticky="nsew", padx=(3, 6), pady=6)

        self._open_spout()
        self.after(1000, self._discover_spout_senders)

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

    def _on_tool_change(self, tool: str) -> None:
        logger.info("Tool selected: %s", tool)

    def _update_json(self) -> None:
        data = {
            "spout": {
                "sender_name": self.workspace.spout_row.get_value(),
                "status": "connected" if self._spout_source.is_open else "disconnected",
            }
        }
        self.workspace.update_json(data)
