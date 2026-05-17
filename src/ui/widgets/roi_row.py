from __future__ import annotations

from typing import Callable

import customtkinter as ctk

TEXT = "#eaeaea"
SURFACE = "#16213e"
HIGHLIGHT = "#0f3460"
RED = "#e74c3c"
BLUE = "#3498db"

TYPE_COLORS = {
    "health_bar": "#2ecc71",
    "timer": "#f39c12",
    "text": "#9b59b6",
}


class ROIRow(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        roi,
        on_delete: Callable[[str], None] = None,
        on_select: Callable[[str], None] = None,
        **kwargs,
    ):
        super().__init__(parent, corner_radius=6, fg_color=SURFACE, **kwargs)

        self._roi = roi
        self._on_delete = on_delete
        self._on_select = on_select

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        type_color = TYPE_COLORS.get(roi.tool_type, TEXT)
        self._badge = ctk.CTkLabel(
            self,
            text=roi.tool_type.replace("_", " ").upper(),
            font=("", 9, "bold"),
            text_color=type_color,
            width=90,
            corner_radius=4,
            fg_color=HIGHLIGHT,
        )
        self._badge.grid(row=0, column=0, sticky="w", padx=(8, 4), pady=4)

        self._name = ctk.CTkLabel(
            self,
            text=roi.name,
            font=("", 11, "bold"),
            text_color=TEXT,
        )
        self._name.grid(row=0, column=0, sticky="w", padx=(96, 4), pady=4)

        coords = ctk.CTkLabel(
            self,
            text=f"{roi.x}, {roi.y}, {roi.width}x{roi.height}",
            font=("", 10),
            text_color="#888888",
        )
        coords.grid(row=0, column=0, sticky="e", padx=(4, 4), pady=4)

        self._del_btn = ctk.CTkButton(
            self,
            text="X",
            width=24,
            height=24,
            corner_radius=4,
            fg_color=RED,
            hover_color="#c0392b",
            text_color="#fff",
            font=("", 10, "bold"),
            command=lambda: self._on_delete and self._on_delete(roi.id),
        )
        self._del_btn.grid(row=0, column=1, padx=(4, 8), pady=4)

        self.bind("<Button-1>", lambda e: self._on_select and self._on_select(roi.id))
        for w in [self._badge, self._name, coords, self._del_btn]:
            w.bind("<Button-1>", lambda e: self._on_select and self._on_select(roi.id))
