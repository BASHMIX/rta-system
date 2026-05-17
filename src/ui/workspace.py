from __future__ import annotations

import json

import customtkinter as ctk

from src.ui.widgets.connection_row import ConnectionRow

TEXT = "#eaeaea"
BG_DARK = "#0d0d1a"


class Workspace(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, corner_radius=10, fg_color="#16213e", **kwargs)

        # --- Connection Header Row 1: OBS ws ---
        self.obs_row = ConnectionRow(self, "OBS ws", ["127.0.0.1"])
        self.obs_row.pack(fill="x", padx=12, pady=(12, 4))

        port_frame = ctk.CTkFrame(self, fg_color="transparent")
        port_frame.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkLabel(port_frame, text="PORT", text_color=TEXT, font=("", 12)).pack(
            side="left", padx=(0, 6)
        )
        self.port_entry = ctk.CTkEntry(
            port_frame, placeholder_text="4455", width=80, corner_radius=6
        )
        self.port_entry.pack(side="left")

        # --- Connection Header Row 2: Spout ---
        self.spout_row = ConnectionRow(self, "Spoutsenders", [])
        self.spout_row.pack(fill="x", padx=12, pady=(0, 12))

        # --- Video Canvas ---
        self.canvas = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=8)
        self.canvas.pack(fill="both", expand=True, padx=12, pady=(0, 12))

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
