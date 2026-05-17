from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

import numpy as np

from src.roi import ROI


@dataclass
class AnalysisResult:
    roi_name: str
    tool_type: str
    value: Any
    timestamp: float


class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, roi: ROI, frame: np.ndarray) -> Optional[AnalysisResult]:
        ...
