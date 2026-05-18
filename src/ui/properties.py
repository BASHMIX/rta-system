from __future__ import annotations

from tkinter import messagebox
from typing import Callable, Optional

import customtkinter as ctk

from src.roi import OBSTarget, ROI, OBS_ACTIONS_SOURCE, OBS_ACTIONS_FILTER

TEXT = "#eaeaea"
SURFACE = "#16213e"
HIGHLIGHT = "#0f3460"
GREEN = "#2ecc71"
BLUE = "#3498db"
ORANGE = "#e67e22"


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
        self._obs_sources: list[str] = []

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
        self._source_menu = ctk.CTkOptionMenu(
            self,
            values=["Select source"],
            variable=self._source_var,
            corner_radius=6,
            fg_color=HIGHLIGHT,
            button_color=HIGHLIGHT,
            button_hover_color="#1a5276",
            text_color=TEXT,
            command=self._on_source_selected,
        )
        self._source_menu.pack(fill="x", padx=12, pady=(0, 4))

        # --- OBS Source Action ---
        self._source_action_var = ctk.StringVar(value="visibility_on")
        self._source_action_menu = ctk.CTkOptionMenu(
            self,
            values=["Show", "Hide"],
            variable=self._source_action_var,
            corner_radius=6,
            fg_color=HIGHLIGHT,
            button_color=HIGHLIGHT,
            button_hover_color="#1a5276",
            text_color=TEXT,
        )
        self._source_action_menu.pack(fill="x", padx=12, pady=(0, 8))

        # --- OBS Filter Checkbox + Dropdown ---
        filter_header = ctk.CTkFrame(self, fg_color="transparent")
        filter_header.pack(fill="x", padx=12, pady=(4, 4))

        self._filter_enabled = ctk.BooleanVar(value=False)
        self._filter_check = ctk.CTkCheckBox(
            filter_header,
            text="Attach to Filter",
            variable=self._filter_enabled,
            text_color=TEXT,
            corner_radius=4,
            command=self._on_filter_toggle,
        )
        self._filter_check.pack(side="left")

        self._filter_var = ctk.StringVar(value="")
        self._filter_menu = ctk.CTkOptionMenu(
            self,
            values=["No filters"],
            variable=self._filter_var,
            corner_radius=6,
            fg_color=HIGHLIGHT,
            button_color=HIGHLIGHT,
            button_hover_color="#1a5276",
            text_color=TEXT,
            state="disabled",
        )
        self._filter_menu.pack(fill="x", padx=12, pady=(0, 4))

        self._filter_action_var = ctk.StringVar(value="filter_enable")
        self._filter_action_menu = ctk.CTkOptionMenu(
            self,
            values=["Enable", "Disable"],
            variable=self._filter_action_var,
            corner_radius=6,
            fg_color=HIGHLIGHT,
            button_color=HIGHLIGHT,
            button_hover_color="#1a5276",
            text_color=TEXT,
            state="disabled",
        )
        self._filter_action_menu.pack(fill="x", padx=12, pady=(0, 8))

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

    def set_obs_sources(self, sources: list[str]) -> None:
        self._obs_sources = sources
        self._source_menu.configure(values=sources or ["No sources found"])

    def _on_source_selected(self, source_name: str) -> None:
        if hasattr(self, "_filter_enabled"):
            self._filter_enabled.set(False)
            self._on_filter_toggle()

    def _on_filter_toggle(self) -> None:
        if self._filter_enabled.get():
            source_name = self._source_var.get()
            filters = self._get_filters_for_source(source_name) if source_name else []
            self._filter_menu.configure(
                values=filters or ["No filters"],
                state="normal" if filters else "disabled",
            )
            self._filter_action_menu.configure(state="normal" if filters else "disabled")
        else:
            self._filter_menu.configure(state="disabled")
            self._filter_action_menu.configure(state="disabled")
            self._filter_var.set("")

    def _get_filters_for_source(self, source_name: str) -> list[str]:
        from src.obs.client import OBSClient
        client = OBSClient()
        if client.is_connected:
            return client.get_source_filters(source_name)
        return []

    def set_selected_roi(self, roi: Optional[ROI]) -> None:
        self._selected_roi = roi
        if roi:
            self._name_var.set(roi.name)
            self._x_var.set(str(roi.x))
            self._y_var.set(str(roi.y))
            self._w_var.set(str(roi.width))
            self._h_var.set(str(roi.height))
            self._source_var.set(roi.obs_target.name)
            if roi.obs_target.type == "filter":
                self._filter_enabled.set(True)
                self._filter_var.set(roi.obs_target.name)
                self._filter_action_var.set(roi.obs_target.action)
                self._on_filter_toggle()
            else:
                self._filter_enabled.set(False)
                self._filter_var.set("")
                self._on_filter_toggle()
            source_action_label = "Show" if roi.obs_target.action == "visibility_on" else "Hide"
            self._source_action_var.set(source_action_label)

    def update_coords(self, x: int, y: int, w: int, h: int) -> None:
        self._x_var.set(str(x))
        self._y_var.set(str(y))
        self._w_var.set(str(w))
        self._h_var.set(str(h))

    def _do_add_roi(self) -> None:
        if not self._on_add_roi:
            return
        
        # Enforce minimum size
        w = max(10, int(self._w_var.get() or "10"))
        h = max(10, int(self._h_var.get() or "10"))
        
        source_name = self._source_var.get()
        if self._filter_enabled.get():
            obs_target = OBSTarget(
                type="filter",
                name=self._filter_var.get(),
                source=source_name,
                action=self._filter_action_var.get(),
            )
        else:
            action = "visibility_on" if self._source_action_var.get() == "Show" else "visibility_off"
            obs_target = OBSTarget(
                type="source",
                name=source_name,
                source="",
                action=action,
            )
        roi = ROI(
            name=self._name_var.get(),
            x=int(self._x_var.get() or "0"),
            y=int(self._y_var.get() or "0"),
            width=w,
            height=h,
            obs_target=obs_target,
        )
        self._on_add_roi(roi)

    def _do_mirror(self) -> None:
        if self._on_mirror and self._selected_roi:
            self._on_mirror(self._selected_roi)

    def _do_save(self) -> None:
        if self._on_save:
            self._on_save()
            messagebox.showinfo("Config Saved", "Configuration saved to config.json")
