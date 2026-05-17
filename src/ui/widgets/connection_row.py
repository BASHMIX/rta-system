from __future__ import annotations

import customtkinter as ctk

TEXT = "#eaeaea"
GREEN = "#2ecc71"
GRAY = "#555555"


class ConnectionRow(ctk.CTkFrame):
    def __init__(self, parent, label: str, options: list[str] = None, command=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.label = ctk.CTkLabel(self, text=label, text_color=TEXT, font=("", 13, "bold"))
        self.label.pack(side="left", padx=(0, 8))

        self.dropdown = ctk.CTkOptionMenu(
            self,
            values=options or ["No senders"],
            command=command,
            corner_radius=6,
            fg_color="#0f3460",
            button_color="#0f3460",
            button_hover_color="#1a5276",
            text_color=TEXT,
        )
        self.dropdown.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.indicator = ctk.CTkFrame(
            self, width=12, height=12, corner_radius=6, fg_color=GRAY
        )
        self.indicator.pack(side="right", padx=(0, 4))

    def set_options(self, opts: list[str]) -> None:
        if opts:
            current = self.dropdown.get()
            self.dropdown.configure(values=opts)
            if current not in opts:
                self.dropdown.set(opts[0])

    def get_value(self) -> str:
        return self.dropdown.get()

    def set_value(self, val: str) -> None:
        self.dropdown.set(val)

    def set_connected(self, connected: bool) -> None:
        self.indicator.configure(fg_color=GREEN if connected else GRAY)
