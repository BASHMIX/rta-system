from __future__ import annotations

import customtkinter as ctk

HIGHLIGHT = "#e94560"
SURFACE = "#16213e"
TEXT = "#eaeaea"


class ToggleGroup(ctk.CTkFrame):
    def __init__(self, parent, options: list[tuple[str, str]], command=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._command = command
        self._selected: str | None = None
        self._buttons: dict[str, ctk.CTkButton] = {}

        for i, (label, icon) in enumerate(options):
            btn = ctk.CTkButton(
                self,
                text=f"{icon}  {label}",
                corner_radius=8,
                fg_color=SURFACE,
                hover_color="#1a2744",
                text_color=TEXT,
                anchor="w",
                command=lambda lbl=label: self._select(lbl),
            )
            btn.pack(fill="x", pady=(0, 6))
            self._buttons[label] = btn

    def _select(self, label: str) -> None:
        self._selected = label
        for lbl, btn in self._buttons.items():
            if lbl == label:
                btn.configure(fg_color=HIGHLIGHT)
            else:
                btn.configure(fg_color=SURFACE)
        if self._command:
            self._command(label)

    def get_selected(self) -> str | None:
        return self._selected

    def set_selected(self, label: str) -> None:
        if label in self._buttons:
            self._select(label)
