from __future__ import annotations

import customtkinter as ctk

from src.ui.widgets.toggle_group import ToggleGroup

TOOLS = [
    ("123 numbers", "123"),
    ("ABC Text", "ABC"),
    ("Gradient", "\u25a0"),
    ("Pixel", "\u25a4"),
]


class ToolsPanel(ctk.CTkFrame):
    def __init__(self, parent, on_tool_change=None, **kwargs):
        super().__init__(parent, corner_radius=10, fg_color="#16213e", **kwargs)

        title = ctk.CTkLabel(
            self,
            text="Tools",
            font=("", 16, "bold"),
            text_color="#eaeaea",
        )
        title.pack(pady=(16, 16))

        self.toggle = ToggleGroup(self, TOOLS, command=on_tool_change)
        self.toggle.pack(fill="x", padx=12)
