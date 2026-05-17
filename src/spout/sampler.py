from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class ColorSample:
    x: int
    y: int
    r: int
    g: int
    b: int
    h: int
    s: int
    v: int


def sample_pixel(frame: np.ndarray, x: int, y: int) -> ColorSample:
    h_img, w_img = frame.shape[:2]
    cx = max(0, min(x, w_img - 1))
    cy = max(0, min(y, h_img - 1))
    rgba = frame[cy, cx]
    r, g, b, _ = int(rgba[0]), int(rgba[1]), int(rgba[2]), int(rgba[3])
    rgb_pixel = np.array([[[r, g, b]]], dtype=np.uint8)
    hsv = cv2.cvtColor(rgb_pixel, cv2.COLOR_RGB2HSV)
    h_val, s_val, v_val = int(hsv[0, 0, 0]), int(hsv[0, 0, 1]), int(hsv[0, 0, 2])
    return ColorSample(x=cx, y=cy, r=r, g=g, b=b, h=h_val, s=s_val, v=v_val)


def sample_batch(
    frame: np.ndarray, points: list[tuple[int, int]]
) -> list[ColorSample]:
    return [sample_pixel(frame, x, y) for x, y in points]


def format_sample(sample: ColorSample) -> str:
    return (
        f"({sample.x:>4}, {sample.y:>4}): "
        f"RGB({sample.r:>3}, {sample.g:>3}, {sample.b:>3}) "
        f"HSV({sample.h:>3}, {sample.s:>3}, {sample.v:>3})"
    )
