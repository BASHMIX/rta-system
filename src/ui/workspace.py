from __future__ import annotations

from typing import Callable, Optional

import customtkinter as ctk
from PIL import Image

from src.ui.drawing_canvas import DrawingCanvas
from src.ui.roi_list_panel import ROIListPanel
from src.ui.widgets.connection_row import ConnectionRow

TEXT = "#eaeaea"
BG_DARK = "#0d0d1a"
HIGHLIGHT = "#0f3460"
GREEN = "#2ecc71"
RED = "#e74c3c"


class Workspace(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        obs_connect_cb=None,
        spout_select_cb=None,
        on_roi_delete=None,
        on_roi_select=None,
        **kwargs,
    ):
        super().__init__(parent, corner_radius=10, fg_color="#16213e", **kwargs)

        self._obs_connect_cb = obs_connect_cb
        self._obs_connected = False

        # --- Top bar: OBS + Spout connections ---
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=12, pady=(8, 4))

        obs_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        obs_frame.pack(side="left", fill="x", expand=True)

        self.obs_row = ConnectionRow(
            obs_frame,
            "OBS ws",
            ["127.0.0.1", "localhost"],
            command=lambda val: self._on_obs_ip_change(val),
        )
        self.obs_row.pack(fill="x", pady=(0, 4))

        port_frame = ctk.CTkFrame(obs_frame, fg_color="transparent")
        port_frame.pack(fill="x")
        ctk.CTkLabel(port_frame, text="PORT", text_color=TEXT, font=("", 11)).pack(
            side="left", padx=(0, 6)
        )
        self.port_entry = ctk.CTkEntry(
            port_frame, placeholder_text="4455", width=70, corner_radius=6,
        )
        self.port_entry.pack(side="left", padx=(0, 6))

        self.obs_btn = ctk.CTkButton(
            port_frame,
            text="Connect",
            width=80,
            corner_radius=6,
            fg_color=GREEN,
            hover_color="#27ae60",
            text_color="#ffffff",
            command=self._toggle_obs,
        )
        self.obs_btn.pack(side="left")

        spout_frame = ctk.CTkFrame(top_bar, fg_color="transparent", width=200)
        spout_frame.pack(side="right", fill="x")

        self.spout_row = ConnectionRow(
            spout_frame,
            "Spout",
            [],
            command=spout_select_cb,
        )
        self.spout_row.pack(fill="x")

        # --- Main area: Left panel (ROI list) + Center (canvas) ---
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=12, pady=(4, 8))

        # Left panel: ROI list with (X) delete buttons
        self.roi_list = ROIListPanel(
            main_frame,
            width=200,
            on_delete=on_roi_delete,
            on_select=on_roi_select,
        )
        self.roi_list.pack(side="left", fill="y", padx=(0, 8))

        # Center: Drawing canvas (16:9)
        self.canvas = DrawingCanvas(main_frame)
        self.canvas.pack(side="left", fill="both", expand=True)

    def _on_obs_ip_change(self, ip: str) -> None:
        pass

    def _toggle_obs(self) -> None:
        if self._obs_connected:
            self._obs_connected = False
            self.obs_btn.configure(text="Connect", fg_color=GREEN, hover_color="#27ae60")
            self.set_obs_connected(False)
            if self._obs_connect_cb:
                self._obs_connect_cb(False)
        else:
            ok = True
            if self._obs_connect_cb:
                ok = self._obs_connect_cb(True)
            if ok:
                self._obs_connected = True
                self.obs_btn.configure(text="Disconnect", fg_color=RED, hover_color="#c0392b")
                self.set_obs_connected(True)

    def refresh_spout_list(self, senders: list[str]) -> None:
        self.spout_row.set_options(senders)

    def set_spout_connected(self, connected: bool) -> None:
        self.spout_row.set_connected(connected)

    def set_obs_connected(self, connected: bool) -> None:
        self.obs_row.set_connected(connected)

    def set_canvas_image(self, pil_img: Optional[Image.Image]) -> None:
        pass
