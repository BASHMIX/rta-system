from __future__ import annotations

from tkinter import messagebox
from typing import Callable, Optional

import customtkinter as ctk

from src.roi import ROI

TEXT = "#eaeaea"
SURFACE = "#16213e"
HIGHLIGHT = "#0f3460"
GREEN = "#2ecc71"
BLUE = "#3498db"
ORANGE = "#e67e22"

OBS_ACTIONS = [
    ("Visibility: On", "visibility_on"),
    ("Visibility: Off", "visibility_off"),
    ("Filter: Enable", "filter_enable"),
    ("Filter: Disable", "filter_disable"),
    ("Source: Show", "source_show"),
    ("Source: Hide", "source_hide"),
]


class PropertiesPanel(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        on_add_roi: Callable = None,
        on_mirror: Callable = None,
        on_save: Callable = None,
        **kwargs,
    ):
        super().__init__(parent, corner_radius=10, fg_color=SURFACE, **kwargs)

        self._on_add_roi = on_add_roi
        self._on_mirror = on_mirror
        self._on_save = on_save
        self._selected_roi: Optional[ROI] = None

        # --- ROI Name ---
        ctk.CTkLabel(self, text="ROI Name", font=("", 12, "bold"), text_color=TEXT).pack(
            anchor="w", padx=12, pady=(12, 4)
        )
        self._name_var = ctk.StringVar(value="P1 Health")
        self._name_entry = ctk.CTkEntry(
            self, textvariable=self._name_var, width=180, corner_radius=6,
        )
        self._name_entry.pack(fill="x", padx=12, pady=(0, 8))

        # --- Coordinates ---
        ctk.CTkLabel(
            self, text="Coordinates", font=("", 12, "bold"), text_color=TEXT,
        ).pack(anchor="w", padx=12, pady=(4, 4))

        xy_frame = ctk.CTkFrame(self, fg_color="transparent")
        xy_frame.pack(fill="x", padx=12, pady=(0, 4))

        ctk.CTkLabel(xy_frame, text="X", text_color=TEXT, font=("", 11)).pack(
            side="left", padx=(0, 2)
        )
        self._x_var = ctk.StringVar(value="0")
        self._x_entry = ctk.CTkEntry(
            xy_frame, textvariable=self._x_var, width=60, corner_radius=6,
        )
        self._x_entry.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(xy_frame, text="Y", text_color=TEXT, font=("", 11)).pack(
            side="left", padx=(0, 2)
        )
        self._y_var = ctk.StringVar(value="0")
        self._y_entry = ctk.CTkEntry(
            xy_frame, textvariable=self._y_var, width=60, corner_radius=6,
        )
        self._y_entry.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(xy_frame, text="W", text_color=TEXT, font=("", 11)).pack(
            side="left", padx=(0, 2)
        )
        self._w_var = ctk.StringVar(value="0")
        self._w_entry = ctk.CTkEntry(
            xy_frame, textvariable=self._w_var, width=60, corner_radius=6,
        )
        self._w_entry.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(xy_frame, text="H", text_color=TEXT, font=("", 11)).pack(
            side="left", padx=(0, 2)
        )
        self._h_var = ctk.StringVar(value="0")
        self._h_entry = ctk.CTkEntry(
            xy_frame, textvariable=self._h_var, width=60, corner_radius=6,
        )
        self._h_entry.pack(side="left")

        separator = ctk.CTkFrame(self, height=1, fg_color="#2a2a4a")
        separator.pack(fill="x", padx=12, pady=12)

        # --- OBS Source ---
        ctk.CTkLabel(
            self, text="OBS Source", font=("", 12, "bold"), text_color=TEXT,
        ).pack(anchor="w", padx=12, pady=(4, 4))
        self._source_var = ctk.StringVar(value="")
        self._source_entry = ctk.CTkEntry(
            self, textvariable=self._source_var, placeholder_text="Source name",
            width=180, corner_radius=6,
        )
        self._source_entry.pack(fill="x", padx=12, pady=(0, 8))

        # --- OBS Filter ---
        ctk.CTkLabel(
            self, text="OBS Filter", font=("", 12, "bold"), text_color=TEXT,
        ).pack(anchor="w", padx=12, pady=(4, 4))
        self._filter_var = ctk.StringVar(value="")
        self._filter_entry = ctk.CTkEntry(
            self, textvariable=self._filter_var, placeholder_text="Filter name",
            width=180, corner_radius=6,
        )
        self._filter_entry.pack(fill="x", padx=12, pady=(0, 8))

        # --- OBS Action ---
        ctk.CTkLabel(
            self, text="Action", font=("", 12, "bold"), text_color=TEXT,
        ).pack(anchor="w", padx=12, pady=(4, 4))
        self._action_var = ctk.StringVar(value="visibility_on")
        self._action_menu = ctk.CTkOptionMenu(
            self,
            values=[label for label, _ in OBS_ACTIONS],
            variable=self._action_var,
            corner_radius=6,
            fg_color=HIGHLIGHT,
            button_color=HIGHLIGHT,
            button_hover_color="#1a5276",
            text_color=TEXT,
        )
        self._action_menu.pack(fill="x", padx=12, pady=(0, 8))
        self._action_menu.set("Visibility: On")

        separator2 = ctk.CTkFrame(self, height=1, fg_color="#2a2a4a")
        separator2.pack(fill="x", padx=12, pady=12)

        # --- Buttons ---
        self._add_btn = ctk.CTkButton(
            self,
            text="Add ROI",
            width=150,
            corner_radius=6,
            fg_color=BLUE,
            hover_color="#2980b9",
            text_color="#fff",
            command=self._do_add_roi,
        )
        self._add_btn.pack(pady=(0, 8))

        self._mirror_btn = ctk.CTkButton(
            self,
            text="Mirror to P2",
            width=150,
            corner_radius=6,
            fg_color=HIGHLIGHT,
            hover_color="#1a5276",
            text_color=TEXT,
            command=self._do_mirror,
        )
        self._mirror_btn.pack(pady=(0, 8))

        self._save_btn = ctk.CTkButton(
            self,
            text="Save Config",
            width=150,
            corner_radius=6,
            fg_color=GREEN,
            hover_color="#27ae60",
            text_color="#fff",
            command=self._do_save,
        )
        self._save_btn.pack(pady=(0, 12))

    def set_selected_roi(self, roi: Optional[ROI]) -> None:
        self._selected_roi = roi
        if roi:
            self._name_var.set(roi.name)
            self._x_var.set(str(roi.x))
            self._y_var.set(str(roi.y))
            self._w_var.set(str(roi.width))
            self._h_var.set(str(roi.height))
            self._source_var.set(roi.obs_source)
            self._filter_var.set(roi.obs_filter)
            action_label = next(
                (label for label, val in OBS_ACTIONS if val == roi.obs_action),
                "Visibility: On",
            )
            self._action_var.set(action_label)

    def update_coords(self, x: int, y: int, w: int, h: int) -> None:
        self._x_var.set(str(x))
        self._y_var.set(str(y))
        self._w_var.set(str(w))
        self._h_var.set(str(h))

    def _do_add_roi(self) -> None:
        if not self._on_add_roi:
            return
        roi = ROI(
            name=self._name_var.get(),
            x=int(self._x_var.get() or "0"),
            y=int(self._y_var.get() or "0"),
            width=int(self._w_var.get() or "0"),
            height=int(self._h_var.get() or "0"),
            obs_source=self._source_var.get(),
            obs_filter=self._filter_var.get(),
            obs_action=self._action_var.get(),
        )
        self._on_add_roi(roi)

    def _do_mirror(self) -> None:
        if self._on_mirror and self._selected_roi:
            self._on_mirror(self._selected_roi)

    def _do_save(self) -> None:
        if self._on_save:
            self._on_save()
            messagebox.showinfo("Config Saved", "Configuration saved to config.json")
