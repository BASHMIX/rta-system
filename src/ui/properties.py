from __future__ import annotations

import customtkinter as ctk

TEXT = "#eaeaea"
SURFACE = "#16213e"
HIGHLIGHT = "#0f3460"


class PropertiesPanel(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, corner_radius=10, fg_color=SURFACE, **kwargs)

        # --- Coordinates ---
        coord_title = ctk.CTkLabel(
            self, text="Coordinates", font=("", 16, "bold"), text_color=TEXT
        )
        coord_title.pack(pady=(16, 12), padx=12, anchor="w")

        xy_frame = ctk.CTkFrame(self, fg_color="transparent")
        xy_frame.pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkLabel(xy_frame, text="X", text_color=TEXT, font=("", 12)).pack(
            side="left", padx=(0, 4)
        )
        self.x_entry = ctk.CTkEntry(
            xy_frame, placeholder_text="0", width=80, corner_radius=6
        )
        self.x_entry.pack(side="left", padx=(0, 16))

        ctk.CTkLabel(xy_frame, text="Y", text_color=TEXT, font=("", 12)).pack(
            side="left", padx=(0, 4)
        )
        self.y_entry = ctk.CTkEntry(
            xy_frame, placeholder_text="0", width=80, corner_radius=6
        )
        self.y_entry.pack(side="left")

        separator = ctk.CTkFrame(self, height=1, fg_color="#2a2a4a")
        separator.pack(fill="x", padx=12, pady=12)

        # --- Actions ---
        actions_title = ctk.CTkLabel(
            self, text="Actions", font=("", 16, "bold"), text_color=TEXT
        )
        actions_title.pack(pady=(0, 12), padx=12, anchor="w")

        ctk.CTkLabel(self, text="Source", text_color=TEXT, font=("", 12)).pack(
            anchor="w", padx=12, pady=(0, 4)
        )
        self.source_dropdown = ctk.CTkOptionMenu(
            self,
            values=["Select source"],
            corner_radius=6,
            fg_color=HIGHLIGHT,
            button_color=HIGHLIGHT,
            button_hover_color="#1a5276",
            text_color=TEXT,
        )
        self.source_dropdown.pack(fill="x", padx=12, pady=(0, 12))

        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=12, pady=(0, 4))
        self.filter_check = ctk.CTkCheckBox(
            filter_frame, text="Filter", text_color=TEXT, corner_radius=4
        )
        self.filter_check.pack(side="left", padx=(0, 8))
        self.filter_dropdown = ctk.CTkOptionMenu(
            filter_frame,
            values=["Select filter"],
            corner_radius=6,
            fg_color=HIGHLIGHT,
            button_color=HIGHLIGHT,
            button_hover_color="#1a5276",
            text_color=TEXT,
        )
        self.filter_dropdown.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(self, text="Action", text_color=TEXT, font=("", 12)).pack(
            anchor="w", padx=12, pady=(12, 4)
        )
        self.action_dropdown = ctk.CTkOptionMenu(
            self,
            values=["Visibility: on", "Off", "Boolean"],
            corner_radius=6,
            fg_color=HIGHLIGHT,
            button_color=HIGHLIGHT,
            button_hover_color="#1a5276",
            text_color=TEXT,
        )
        self.action_dropdown.pack(fill="x", padx=12, pady=(0, 12))
