from __future__ import annotations

from typing import Callable, Optional

import customtkinter as ctk
from PIL import Image, ImageTk

CENTER_X = 960
SCREEN_W = 1920
SCREEN_H = 1080

TEXT = "#eaeaea"
ACCENT = "#0f3460"
BOX_COLOR = "#00d4ff"
BOX_FILL = (0, 212, 255, 40)
GUIDE_COLOR = "#333355"


class DrawingCanvas(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, corner_radius=8, fg_color="#0d0d1a", **kwargs)

        self._screenshot: Optional[Image.Image] = None
        self._display_img: Optional[ImageTk.PhotoImage] = None
        self._overlay_img: Optional[ImageTk.PhotoImage] = None
        self._rois = []
        self._drawing = False
        self._start_x = 0
        self._start_y = 0
        self._current_rect = None
        self._on_coords_change: Optional[Callable[[int, int, int, int], None]] = None
        self._mode = "setup"

        self._canvas = ctk.CTkLabel(self, text="", fg_color="transparent")
        self._canvas.pack(fill="both", expand=True)

        self._canvas.bind("<Button-1>", self._on_press)
        self._canvas.bind("<B1-Motion>", self._on_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)
        self._canvas.bind("<Configure>", self._on_resize)

        self._placeholder = ctk.CTkLabel(
            self,
            text="Upload a screenshot to begin",
            text_color="#444444",
            font=("", 16),
        )
        self._placeholder.place(relx=0.5, rely=0.5, anchor="center")

    def set_coords_callback(self, cb: Callable[[int, int, int, int], None]) -> None:
        self._on_coords_change = cb

    def set_mode(self, mode: str) -> None:
        self._mode = mode
        if mode == "live":
            self._canvas.configure(image="", text="")
            self._placeholder.place_forget()

    def load_screenshot(self, path: str) -> None:
        self._screenshot = Image.open(path).convert("RGBA")
        self._placeholder.place_forget()
        self._render()

    def set_rois(self, rois: list) -> None:
        self._rois = rois
        if self._screenshot:
            self._render()

    def add_roi(self, roi) -> None:
        self._rois.append(roi)
        if self._screenshot:
            self._render()

    def remove_roi(self, roi_id: str) -> None:
        self._rois = [r for r in self._rois if r.id != roi_id]
        if self._screenshot:
            self._render()

    def _on_resize(self, event) -> None:
        if self._screenshot and self._mode == "setup":
            self._render()

    def _screen_to_canvas(self, sx: int, sy: int) -> tuple[int, int]:
        cw = self._canvas.winfo_width()
        ch = self._canvas.winfo_height()
        if cw <= 1 or ch <= 1:
            return 0, 0
        scale = min(cw / SCREEN_W, ch / SCREEN_H)
        ox = (cw - SCREEN_W * scale) / 2
        oy = (ch - SCREEN_H * scale) / 2
        return int(sx * scale + ox), int(sy * scale + oy)

    def _canvas_to_screen(self, cx: int, cy: int) -> tuple[int, int]:
        cw = self._canvas.winfo_width()
        ch = self._canvas.winfo_height()
        if cw <= 1 or ch <= 1:
            return 0, 0
        scale = min(cw / SCREEN_W, ch / SCREEN_H)
        ox = (cw - SCREEN_W * scale) / 2
        oy = (ch - SCREEN_H * scale) / 2
        return int((cx - ox) / scale), int((cy - oy) / scale)

    def _on_press(self, event) -> None:
        if self._mode != "setup" or not self._screenshot:
            return
        self._drawing = True
        self._start_x, self._start_y = self._canvas_to_screen(event.x, event.y)
        self._current_rect = None

    def _on_drag(self, event) -> None:
        if not self._drawing or self._mode != "setup":
            return
        cx, cy = self._canvas_to_screen(event.x, event.y)
        x = min(self._start_x, cx)
        y = min(self._start_y, cy)
        w = abs(cx - self._start_x)
        h = abs(cy - self._start_y)
        self._current_rect = (x, y, w, h)
        if self._on_coords_change:
            self._on_coords_change(x, y, w, h)
        self._render()

    def _on_release(self, event) -> None:
        self._drawing = False

    def _render(self) -> None:
        if not self._screenshot or self._mode != "setup":
            return

        cw = self._canvas.winfo_width()
        ch = self._canvas.winfo_height()
        if cw <= 1 or ch <= 1:
            return

        scale = min(cw / SCREEN_W, ch / SCREEN_H)
        dw = int(SCREEN_W * scale)
        dh = int(SCREEN_H * scale)

        base = self._screenshot.resize((dw, dh), Image.LANCZOS).copy()
        from PIL import ImageDraw

        draw = ImageDraw.Draw(base)

        cx_guide = int(CENTER_X * scale)
        draw.line([(cx_guide, 0), (cx_guide, dh)], fill=GUIDE_COLOR, width=2)

        for roi in self._rois:
            rx1, ry1 = self._screen_to_canvas(roi.x, roi.y)
            rx2, ry2 = self._screen_to_canvas(roi.x + roi.width, roi.y + roi.height)
            draw.rectangle([rx1, ry1, rx2, ry2], outline=BOX_COLOR, width=2)
            draw.text((rx1 + 4, ry1 - 16), roi.name, fill=BOX_COLOR)

        if self._current_rect:
            x, y, w, h = self._current_rect
            cx1, cy1 = self._screen_to_canvas(x, y)
            cx2, cy2 = self._screen_to_canvas(x + w, y + h)
            draw.rectangle([cx1, cy1, cx2, cy2], outline="#ff6600", width=2)

        self._display_img = ImageTk.PhotoImage(base)
        self._canvas.configure(image=self._display_img, text="")
