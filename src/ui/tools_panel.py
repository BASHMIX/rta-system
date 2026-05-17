from __future__ import annotations

from tkinter import filedialog
from typing import Callable

import customtkinter as ctk

TEXT = "#eaeaea"
SURFACE = "#16213e"
HIGHLIGHT = "#0f3460"
GREEN = "#2ecc71"
ORANGE = "#e67e22"

TOOL_TYPES = [
    ("Health Bar", "health_bar"),
    ("Timer", "timer"),
    ("Text", "text"),
]


class ToolsPanel(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        on_tool_change: Callable[[str], None] = None,
        on_upload: Callable[[str], None] = None,
        on_mode_toggle: Callable[[str], None] = None,
        on_frame_skip: Callable[[int], None] = None,
        **kwargs,
    ):
        super().__init__(parent, corner_radius=10, fg_color=SURFACE, **kwargs)

        self._on_tool_change = on_tool_change
        self._on_upload = on_upload
        self._on_mode_toggle = on_mode_toggle
        self._on_frame_skip = on_frame_skip
        self._mode = "setup"

        title = ctk.CTkLabel(
            self, text="Tools", font=("", 16, "bold"), text_color=TEXT,
        )
        title.pack(pady=(12, 8))

        self._upload_btn = ctk.CTkButton(
            self,
            text="Upload Screenshot",
            width=150,
            corner_radius=6,
            fg_color=HIGHLIGHT,
            hover_color="#1a5276",
            text_color=TEXT,
            command=self._do_upload,
        )
        self._upload_btn.pack(pady=(0, 12))

        sep = ctk.CTkFrame(self, height=1, fg_color="#2a2a4a")
        sep.pack(fill="x", padx=12, pady=8)

        type_label = ctk.CTkLabel(
            self, text="Tool Type", font=("", 12, "bold"), text_color=TEXT,
        )
        type_label.pack(anchor="w", padx=12, pady=(4, 4))

        self._tool_var = ctk.StringVar(value="health_bar")
        for label, value in TOOL_TYPES:
            rb = ctk.CTkRadioButton(
                self,
                text=label,
                variable=self._tool_var,
                value=value,
                text_color=TEXT,
                command=lambda v=value: self._on_tool_change and self._on_tool_change(v),
            )
            rb.pack(anchor="w", padx=16, pady=2)

        sep2 = ctk.CTkFrame(self, height=1, fg_color="#2a2a4a")
        sep2.pack(fill="x", padx=12, pady=12)

        mode_label = ctk.CTkLabel(
            self, text="Mode", font=("", 12, "bold"), text_color=TEXT,
        )
        mode_label.pack(anchor="w", padx=12, pady=(4, 4))

        self._mode_btn = ctk.CTkButton(
            self,
            text="SETUP",
            width=150,
            corner_radius=6,
            fg_color=ORANGE,
            hover_color="#d35400",
            text_color="#fff",
            command=self._toggle_mode,
        )
        self._mode_btn.pack(pady=(0, 12))

        sep3 = ctk.CTkFrame(self, height=1, fg_color="#2a2a4a")
        sep3.pack(fill="x", padx=12, pady=8)

        skip_label = ctk.CTkLabel(
            self, text="Frame Skip", font=("", 12, "bold"), text_color=TEXT,
        )
        skip_label.pack(anchor="w", padx=12, pady=(4, 4))

        self._skip_var = ctk.StringVar(value="2")
        self._skip_menu = ctk.CTkOptionMenu(
            self,
            values=[str(i) for i in range(11)],
            variable=self._skip_var,
            corner_radius=6,
            fg_color=HIGHLIGHT,
            button_color=HIGHLIGHT,
            button_hover_color="#1a5276",
            text_color=TEXT,
            command=self._on_skip_change,
        )
        self._skip_menu.pack(fill="x", padx=12, pady=(0, 8))

    def _do_upload(self) -> None:
        path = filedialog.askopenfilename(
            title="Select Screenshot",
            filetypes=[("Images", "*.jpg *.jpeg *.png")],
        )
        if path and self._on_upload:
            self._on_upload(path)

    def _toggle_mode(self) -> None:
        if self._mode == "setup":
            self._mode = "live"
            self._mode_btn.configure(text="LIVE", fg_color=GREEN, hover_color="#27ae60")
        else:
            self._mode = "setup"
            self._mode_btn.configure(text="SETUP", fg_color=ORANGE, hover_color="#d35400")
        if self._on_mode_toggle:
            self._on_mode_toggle(self._mode)

    def _on_skip_change(self, val: str) -> None:
        if self._on_frame_skip:
            self._on_frame_skip(int(val))

    def get_tool_type(self) -> str:
        return self._tool_var.get()

    def get_frame_skip(self) -> int:
        return int(self._skip_var.get())
