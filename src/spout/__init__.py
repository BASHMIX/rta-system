from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class SpoutFrame:
    width: int
    height: int
    data: np.ndarray
    timestamp: float


class FrameSource(ABC):
    @abstractmethod
    def open(self) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    @abstractmethod
    def grab(self) -> Optional[SpoutFrame]:
        ...

    @property
    @abstractmethod
    def is_open(self) -> bool:
        ...

    @property
    @abstractmethod
    def frame_width(self) -> int:
        ...

    @property
    @abstractmethod
    def frame_height(self) -> int:
        ...

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *args):
        self.close()
