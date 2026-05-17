from __future__ import annotations

import time
from typing import Optional

import numpy as np

from src.roi import ROI
from src.roi.base import AnalysisResult, BaseAnalyzer


class TimerAnalyzer(BaseAnalyzer):
    def analyze(self, roi: ROI, frame: np.ndarray) -> Optional[AnalysisResult]:
        cropped = roi.crop(frame)
        if cropped.size == 0:
            return None

        try:
            import pytesseract
            from PIL import Image
            gray = np.mean(cropped, axis=2).astype(np.uint8)
            pil_img = Image.fromarray(gray)
            text = pytesseract.image_to_string(pil_img, config="--psm 7 -c tessedit_char_whitelist=0123456789:").strip()
            return AnalysisResult(
                roi_name=roi.name,
                tool_type="timer",
                value=text,
                timestamp=time.perf_counter(),
            )
        except ImportError:
            return AnalysisResult(
                roi_name=roi.name,
                tool_type="timer",
                value="[pytesseract not installed]",
                timestamp=time.perf_counter(),
            )
        except Exception:
            return None
