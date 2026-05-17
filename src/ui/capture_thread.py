from __future__ import annotations

import logging
import queue
import threading
import time
from typing import Any, Callable, Optional

import numpy as np

from src.roi import ROI

logger = logging.getLogger(__name__)


class CaptureThread(threading.Thread):
    def __init__(
        self,
        spout_source,
        analyzers: dict,
        result_queue: queue.Queue,
        interval_ms: int = 33,
    ):
        super().__init__(daemon=True)
        self._spout = spout_source
        self._analyzers = analyzers
        self._result_queue = result_queue
        self._interval = interval_ms / 1000.0
        self._stop_event = threading.Event()

        self._mode = "setup"
        self._frame_skip = 2
        self._skip_counter = 0
        self._rois: list[ROI] = []
        self._rois_lock = threading.Lock()

        self._frame_count = 0
        self._fps_timer = time.perf_counter()

    def run(self) -> None:
        logger.info("Capture thread started")
        while not self._stop_event.is_set():
            frame = self._spout.grab()
            if frame is None:
                self._stop_event.wait(self._interval)
                continue

            self._frame_count += 1

            if self._mode == "live":
                self._skip_counter += 1
                if self._skip_counter <= self._frame_skip:
                    self._stop_event.wait(self._interval)
                    continue
                self._skip_counter = 0
                self._run_analysis(frame)
            else:
                rgb_data = frame.data[:, :, :3]
                self._put_result({
                    "type": "frame",
                    "rgb": rgb_data,
                    "width": frame.width,
                    "height": frame.height,
                })

            now = time.perf_counter()
            elapsed = now - self._fps_timer
            if elapsed >= 2.0:
                fps = self._frame_count / elapsed
                self._put_result({"type": "fps", "fps": round(fps, 1)})
                self._frame_count = 0
                self._fps_timer = now

            self._stop_event.wait(self._interval)

        logger.info("Capture thread stopped")

    def stop(self) -> None:
        self._stop_event.set()

    def set_mode(self, mode: str) -> None:
        self._mode = mode

    def set_frame_skip(self, skip: int) -> None:
        self._frame_skip = skip
        self._skip_counter = 0

    def set_rois(self, rois: list[ROI]) -> None:
        with self._rois_lock:
            self._rois = list(rois)

    def add_roi(self, roi: ROI) -> None:
        with self._rois_lock:
            self._rois.append(roi)

    def remove_roi(self, roi_id: str) -> None:
        with self._rois_lock:
            self._rois = [r for r in self._rois if r.id != roi_id]

    def get_rois(self) -> list[ROI]:
        with self._rois_lock:
            return list(self._rois)

    def _run_analysis(self, frame) -> None:
        with self._rois_lock:
            rois_copy = list(self._rois)

        results = []
        for roi in rois_copy:
            analyzer = self._analyzers.get(roi.tool_type)
            if analyzer:
                try:
                    result = analyzer.analyze(roi, frame)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error("Analysis error for ROI '%s': %s", roi.name, e)

        if results:
            self._put_result({"type": "analysis", "results": results})

    def _put_result(self, data: dict) -> None:
        try:
            self._result_queue.put_nowait(data)
        except queue.Full:
            logger.warning("Result queue full, dropping frame")
