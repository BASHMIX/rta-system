from __future__ import annotations

import json
from typing import Optional

import customtkinter as ctk
from PIL import Image

from src.ui.widgets.connection_row import ConnectionRow

TEXT = "#eaeaea"
BG_DARK = "#0d0d1a"
HIGHLIGHT = "#0f3460"
GREEN = "#2ecc71"
RED = "#e74c3c"


class Workspace(ctk.CTkFrame):
    def __init__(self, parent, obs_connect_cb=None, spout_select_cb=None, **kwargs):
        super().__init__(parent, corner_radius=10, fg_color="#16213e", **kwargs)

        self._obs_connect_cb = obs_connect_cb
        self._obs_connected = False

        # --- Connection Header Row 1: OBS ws ---
        self.obs_row = ConnectionRow(
            self,
            "OBS ws",
            ["127.0.0.1", "localhost"],
            command=lambda val: self._on_obs_ip_change(val),
        )
        self.obs_row.pack(fill="x", padx=12, pady=(12, 4))

        port_frame = ctk.CTkFrame(self, fg_color="transparent")
        port_frame.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkLabel(port_frame, text="PORT", text_color=TEXT, font=("", 12)).pack(
            side="left", padx=(0, 6)
        )
        self.port_entry = ctk.CTkEntry(
            port_frame, placeholder_text="4455", width=80, corner_radius=6
        )
        self.port_entry.pack(side="left", padx=(0, 8))

        self.obs_btn = ctk.CTkButton(
            port_frame,
            text="Connect",
            width=90,
            corner_radius=6,
            fg_color=GREEN,
            hover_color="#27ae60",
            text_color="#ffffff",
            command=self._toggle_obs,
        )
        self.obs_btn.pack(side="left")

        # --- Connection Header Row 2: Spout ---
        self.spout_row = ConnectionRow(
            self,
            "Spoutsenders",
            [],
            command=spout_select_cb,
        )
        self.spout_row.pack(fill="x", padx=12, pady=(0, 12))

        # --- Video Canvas ---
        self.canvas = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=8)
        self.canvas.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.canvas.pack_propagate(False)

        self.canvas_label = ctk.CTkLabel(
            self.canvas,
            text="Video Feed",
            text_color="#444444",
            font=("", 18),
        )
        self.canvas_label.place(relx=0.5, rely=0.5, anchor="center")

        # --- JSON Viewer ---
        json_label = ctk.CTkLabel(
            self, text="Json", text_color=TEXT, font=("", 13, "bold")
        )
        json_label.pack(anchor="w", padx=12, pady=(0, 4))

        self.json_view = ctk.CTkTextbox(
            self,
            height=140,
            corner_radius=8,
            fg_color="#0d0d1a",
            text_color=TEXT,
            font=("Consolas", 11),
        )
        self.json_view.pack(fill="x", padx=12, pady=(0, 12))
        self.json_view.configure(state="disabled")

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

    def set_canvas_image(self, pil_img: Optional[Image.Image]) -> None:
        if pil_img is None:
            self.canvas_label.configure(image="", text="Video Feed")
            return
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw > 10 and ch > 10:
            pil_img.thumbnail((cw, ch), Image.LANCZOS)
        ctk_img = ctk.CTkImage(
            light_image=pil_img,
            dark_image=pil_img,
            size=pil_img.size,
        )
        self.canvas_label.configure(image=ctk_img, text="")

    def refresh_spout_list(self, senders: list[str]) -> None:
        self.spout_row.set_options(senders)

    def set_spout_connected(self, connected: bool) -> None:
        self.spout_row.set_connected(connected)

    def set_obs_connected(self, connected: bool) -> None:
        self.obs_row.set_connected(connected)

    def update_json(self, data: dict) -> None:
        self.json_view.configure(state="normal")
        self.json_view.delete("0.0", "end")
        formatted = json.dumps(data, indent=2, ensure_ascii=False)
        self.json_view.insert("0.0", formatted)
        self.json_view.configure(state="disabled")
