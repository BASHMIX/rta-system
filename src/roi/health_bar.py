from __future__ import annotations

import time
from typing import Optional

import cv2
import numpy as np

from src.roi import ROI
from src.roi.base import AnalysisResult, BaseAnalyzer


class HealthBarAnalyzer(BaseAnalyzer):
    def analyze(self, roi: ROI, frame: np.ndarray) -> Optional[AnalysisResult]:
        cropped = roi.crop(frame)
        if cropped.size == 0:
            return None

        h, w = cropped.shape[:2]
        center_row = cropped[h // 2, :, :]

        hsv = cv2.cvtColor(cropped, cv2.COLOR_RGB2HSV)
        center_hsv = hsv[h // 2, :, :]

        health_mask = (
            (center_hsv[:, 0] >= 0) & (center_hsv[:, 0] <= 25) &
            (center_hsv[:, 1] >= 80) & (center_hsv[:, 2] >= 80)
        )

        health_pixels = 0
        for i in range(w):
            if health_mask[i]:
                health_pixels += 1
            else:
                break

        fill_pct = (health_pixels / w) * 100 if w > 0 else 0

        return AnalysisResult(
            roi_name=roi.name,
            tool_type="health_bar",
            value=round(fill_pct, 1),
            timestamp=time.perf_counter(),
        )
