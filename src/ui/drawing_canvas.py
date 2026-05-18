from __future__ import annotations

from typing import Callable, Optional

import customtkinter as ctk
from PIL import Image, ImageTk

CENTER_X = 960
SCREEN_W = 1920
SCREEN_H = 1080
HANDLE_SIZE = 8
MIN_ROI_SIZE = 10

TEXT = "#eaeaea"
ACCENT = "#0f3460"
BOX_COLOR = "#00d4ff"
BOX_SELECTED = "#ff6600"
BOX_FILL = (0, 212, 255, 40)
GUIDE_COLOR = "#333355"
HANDLE_COLOR = "#ffffff"

RESIZE_CURSORS = {
    "tl": "top_left_corner",
    "tr": "top_right_corner",
    "bl": "bottom_left_corner",
    "br": "bottom_right_corner",
    "t": "top_side",
    "b": "bottom_side",
    "l": "left_side",
    "r": "right_side",
}


class DrawingCanvas(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, corner_radius=8, fg_color="#0d0d1a", **kwargs)

        self._screenshot: Optional[Image.Image] = None
        self._live_frame: Optional[Image.Image] = None
        self._display_img: Optional[ImageTk.PhotoImage] = None
        self._rois = []
        self._selected_roi_id: Optional[str] = None

        self._drawing = False
        self._moving = False
        self._resizing = False
        self._resize_handle: Optional[str] = None
        self._start_x = 0
        self._start_y = 0
        self._move_offset_x = 0
        self._move_offset_y = 0
        self._current_rect = None

        self._on_coords_change: Optional[Callable[[int, int, int, int], None]] = None
        self._on_select: Optional[Callable[[Optional[str]], None]] = None
        self._mode = "setup"
        self._scale_mode = "native"

        self._canvas = ctk.CTkLabel(self, text="", fg_color="transparent")
        self._canvas.pack(fill="both", expand=True)

        self._canvas.bind("<Button-1>", self._on_press)
        self._canvas.bind("<B1-Motion>", self._on_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)
        self._canvas.bind("<Configure>", self._on_resize)
        self._canvas.bind("<Motion>", self._on_hover)

        self._placeholder = ctk.CTkLabel(
            self,
            text="Upload a screenshot to begin",
            text_color="#444444",
            font=("", 16),
        )
        self._placeholder.place(relx=0.5, rely=0.5, anchor="center")

    def set_coords_callback(self, cb: Callable[[int, int, int, int], None]) -> None:
        self._on_coords_change = cb

    def set_select_callback(self, cb: Callable[[Optional[str]], None]) -> None:
        self._on_select = cb

    def set_mode(self, mode: str) -> None:
        self._mode = mode
        if mode == "live":
            self._placeholder.place_forget()

    def set_scale_mode(self, mode: str) -> None:
        self._scale_mode = mode
        self._render()

    def load_screenshot(self, path: str) -> None:
        self._screenshot = Image.open(path).convert("RGBA")
        self._placeholder.place_forget()
        self._render()

    def set_live_frame(self, frame_data) -> None:
        from PIL import Image
        rgb = frame_data[:, :, :3]
        self._live_frame = Image.fromarray(rgb)
        if self._mode == "live":
            self._render()

    def set_rois(self, rois: list) -> None:
        self._rois = rois
        self._render()

    def add_roi(self, roi) -> None:
        self._rois.append(roi)
        self._render()

    def remove_roi(self, roi_id: str) -> None:
        self._rois = [r for r in self._rois if r.id != roi_id]
        if self._selected_roi_id == roi_id:
            self._selected_roi_id = None
        self._render()

    def select_roi(self, roi_id: Optional[str]) -> None:
        self._selected_roi_id = roi_id
        self._render()

    def get_selected_roi(self):
        if self._selected_roi_id:
            return next((r for r in self._rois if r.id == self._selected_roi_id), None)
        return None

    def _on_resize(self, event) -> None:
        self._render()

    def _get_scale_and_offset(self) -> tuple[float, int, int]:
        cw = self._canvas.winfo_width()
        ch = self._canvas.winfo_height()
        if cw <= 1 or ch <= 1:
            return 1.0, 0, 0

        target_w, target_h = self._get_target_resolution()
        scale = min(cw / target_w, ch / target_h)
        dw = int(target_w * scale)
        dh = int(target_h * scale)
        ox = (cw - dw) / 2
        oy = (ch - dh) / 2
        return scale, ox, oy

    def _get_target_resolution(self) -> tuple[int, int]:
        if self._scale_mode == "1080p":
            return 1920, 1080
        elif self._scale_mode == "720p":
            return 1280, 720
        return SCREEN_W, SCREEN_H

    def _screen_to_canvas(self, sx: int, sy: int) -> tuple[int, int]:
        scale, ox, oy = self._get_scale_and_offset()
        return int(sx * scale + ox), int(sy * scale + oy)

    def _canvas_to_screen(self, cx: int, cy: int) -> tuple[int, int]:
        scale, ox, oy = self._get_scale_and_offset()
        return int((cx - ox) / scale), int((cy - oy) / scale)

    def _hit_test(self, cx: int, cy: int) -> tuple[Optional[str], Optional[str]]:
        if self._mode != "setup":
            return None, None

        sx, sy = self._canvas_to_screen(cx, cy)

        for roi in reversed(self._rois):
            handle = self._hit_test_handles(roi, sx, sy)
            if handle:
                return roi.id, handle

        for roi in reversed(self._rois):
            if (roi.x <= sx <= roi.x + roi.width and
                    roi.y <= sy <= roi.y + roi.height):
                return roi.id, "inside"

        return None, None

    def _hit_test_handles(self, roi, sx: int, sy: int) -> Optional[str]:
        hs = HANDLE_SIZE
        x, y, w, h = roi.x, roi.y, roi.width, roi.height

        handles = {
            "tl": (x, y),
            "tr": (x + w, y),
            "bl": (x, y + h),
            "br": (x + w, y + h),
            "t": (x + w // 2, y),
            "b": (x + w // 2, y + h),
            "l": (x, y + h // 2),
            "r": (x + w, y + h // 2),
        }

        for name, (hx, hy) in handles.items():
            if abs(sx - hx) <= hs and abs(sy - hy) <= hs:
                return name
        return None

    def _on_press(self, event) -> None:
        if self._mode != "setup":
            return

        roi_id, hit = self._hit_test(event.x, event.y)

        if roi_id and hit == "inside":
            self._selected_roi_id = roi_id
            self._moving = True
            roi = next((r for r in self._rois if r.id == roi_id), None)
            if roi:
                sx, sy = self._canvas_to_screen(event.x, event.y)
                self._move_offset_x = sx - roi.x
                self._move_offset_y = sy - roi.y
            if self._on_select:
                self._on_select(roi_id)
            self._render()
        elif roi_id and hit in RESIZE_CURSORS:
            self._selected_roi_id = roi_id
            self._resizing = True
            self._resize_handle = hit
            self._start_x, self._start_y = self._canvas_to_screen(event.x, event.y)
            if self._on_select:
                self._on_select(roi_id)
            self._render()
        elif not roi_id:
            self._selected_roi_id = None
            if self._on_select:
                self._on_select(None)
            self._drawing = True
            self._start_x, self._start_y = self._canvas_to_screen(event.x, event.y)
            self._current_rect = None
            self._render()

    def _on_drag(self, event) -> None:
        if self._mode != "setup":
            return

        if self._moving:
            sx, sy = self._canvas_to_screen(event.x, event.y)
            roi = self.get_selected_roi()
            if roi:
                roi.x = max(0, sx - self._move_offset_x)
                roi.y = max(0, sy - self._move_offset_y)
                if self._on_coords_change:
                    self._on_coords_change(roi.x, roi.y, roi.width, roi.height)
                self._render()

        elif self._resizing:
            sx, sy = self._canvas_to_screen(event.x, event.y)
            roi = self.get_selected_roi()
            if roi:
                self._apply_resize(roi, sx, sy)
                if self._on_coords_change:
                    self._on_coords_change(roi.x, roi.y, roi.width, roi.height)
                self._render()

        elif self._drawing:
            cx, cy = self._canvas_to_screen(event.x, event.y)
            x = min(self._start_x, cx)
            y = min(self._start_y, cy)
            w = abs(cx - self._start_x)
            h = abs(cy - self._start_y)
            self._current_rect = (x, y, w, h)
            if self._on_coords_change:
                self._on_coords_change(x, y, w, h)
            self._render()

    def _apply_resize(self, roi, sx: int, sy: int) -> None:
        handle = self._resize_handle
        x, y, w, h = roi.x, roi.y, roi.width, roi.height

        if handle == "br":
            w = max(MIN_ROI_SIZE, sx - x)
            h = max(MIN_ROI_SIZE, sy - y)
        elif handle == "bl":
            new_w = max(MIN_ROI_SIZE, (x + w) - sx)
            x = (x + w) - new_w
            w = new_w
            h = max(MIN_ROI_SIZE, sy - y)
        elif handle == "tr":
            w = max(MIN_ROI_SIZE, sx - x)
            new_h = max(MIN_ROI_SIZE, (y + h) - sy)
            h = new_h
        elif handle == "tl":
            new_w = max(MIN_ROI_SIZE, (x + w) - sx)
            x = (x + w) - new_w
            w = new_w
            new_h = max(MIN_ROI_SIZE, (y + h) - sy)
            y = (y + h) - new_h
            h = new_h
        elif handle == "r":
            w = max(MIN_ROI_SIZE, sx - x)
        elif handle == "l":
            new_w = max(MIN_ROI_SIZE, (x + w) - sx)
            x = (x + w) - new_w
            w = new_w
        elif handle == "b":
            h = max(MIN_ROI_SIZE, sy - y)
        elif handle == "t":
            new_h = max(MIN_ROI_SIZE, (y + h) - sy)
            y = (y + h) - new_h
            h = new_h

        roi.x = x
        roi.y = y
        roi.width = w
        roi.height = h

    def _on_release(self, event) -> None:
        self._drawing = False
        self._moving = False
        self._resizing = False
        self._resize_handle = None

    def _on_hover(self, event) -> None:
        if self._mode != "setup":
            return
        roi_id, hit = self._hit_test(event.x, event.y)
        if hit in RESIZE_CURSORS:
            self._canvas.configure(cursor=RESIZE_CURSORS[hit])
        elif hit == "inside":
            self._canvas.configure(cursor="fleur")
        else:
            self._canvas.configure(cursor="")

    def _render(self) -> None:
        cw = self._canvas.winfo_width()
        ch = self._canvas.winfo_height()
        if cw <= 1 or ch <= 1:
            return

        target_w, target_h = self._get_target_resolution()
        scale, ox, oy = self._get_scale_and_offset()
        if scale <= 0:
            return

        dw = int(target_w * scale)
        dh = int(target_h * scale)

        if self._mode == "live" and self._live_frame:
            base = self._live_frame.resize((dw, dh), Image.LANCZOS).copy()
        elif self._screenshot:
            base = self._screenshot.resize((dw, dh), Image.LANCZOS).copy()
        else:
            return

        from PIL import ImageDraw
        draw = ImageDraw.Draw(base)

        cx_guide = int(CENTER_X * scale)
        draw.line([(cx_guide, 0), (cx_guide, dh)], fill=GUIDE_COLOR, width=2)

        for roi in self._rois:
            is_selected = roi.id == self._selected_roi_id
            color = BOX_SELECTED if is_selected else BOX_COLOR
            rx1, ry1 = self._screen_to_canvas(roi.x, roi.y)
            rx2, ry2 = self._screen_to_canvas(roi.x + roi.width, roi.y + roi.height)
            draw.rectangle([rx1, ry1, rx2, ry2], outline=color, width=3 if is_selected else 2)
            draw.text((rx1 + 4, ry1 - 16), roi.name, fill=color)

            if is_selected:
                self._draw_handles(draw, roi, scale)

        if self._current_rect:
            x, y, w, h = self._current_rect
            cx1, cy1 = self._screen_to_canvas(x, y)
            cx2, cy2 = self._screen_to_canvas(x + w, y + h)
            draw.rectangle([cx1, cy1, cx2, cy2], outline="#ff6600", width=2)

        self._display_img = ImageTk.PhotoImage(base)
        self._canvas.configure(image=self._display_img, text="")

    def _draw_handles(self, draw, roi, scale: float) -> None:
        hs = HANDLE_SIZE
        x, y, w, h = roi.x, roi.y, roi.width, roi.height

        handles = [
            (x, y),
            (x + w, y),
            (x, y + h),
            (x + w, y + h),
            (x + w // 2, y),
            (x + w // 2, y + h),
            (x, y + h // 2),
            (x + w, y + h // 2),
        ]

        for hx, hy in handles:
            cx1, cy1 = self._screen_to_canvas(hx - hs, hy - hs)
            cx2, cy2 = self._screen_to_canvas(hx + hs, hy + hs)
            draw.rectangle([cx1, cy1, cx2, cy2], fill=HANDLE_COLOR, outline="#000000", width=1)
