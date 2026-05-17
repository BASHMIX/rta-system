from __future__ import annotations

from typing import Callable, Optional

import customtkinter as ctk

from src.ui.widgets.roi_row import ROIRow

TEXT = "#eaeaea"
SURFACE = "#16213e"


class ROIListPanel(ctk.CTkScrollableFrame):
    def __init__(
        self,
        parent,
        on_delete: Callable[[str], None] = None,
        on_select: Callable[[str], None] = None,
        **kwargs,
    ):
        super().__init__(parent, corner_radius=8, fg_color=SURFACE, **kwargs)

        self._on_delete = on_delete
        self._on_select = on_select
        self._rows: dict[str, ROIRow] = {}
        self._selected_id: Optional[str] = None

    def set_rois(self, rois: list) -> None:
        for row in self._rows.values():
            row.destroy()
        self._rows.clear()
        for roi in rois:
            self._add_row(roi)

    def add_roi(self, roi) -> None:
        self._add_row(roi)

    def remove_roi(self, roi_id: str) -> None:
        if roi_id in self._rows:
            self._rows[roi_id].destroy()
            del self._rows[roi_id]

    def select_roi(self, roi_id: str) -> None:
        self._selected_id = roi_id
        if self._on_select:
            self._on_select(roi_id)

    def get_selected_id(self) -> Optional[str]:
        return self._selected_id

    def _add_row(self, roi) -> None:
        row = ROIRow(
            self,
            roi,
            on_delete=self._on_delete,
            on_select=lambda rid: self.select_roi(rid),
        )
        row.pack(fill="x", padx=4, pady=2)
        self._rows[roi.id] = row
