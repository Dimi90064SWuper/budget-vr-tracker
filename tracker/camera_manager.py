"""
Camera management for Budget VR Tracker.
"""

import asyncio
import logging
import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional

from .config import Config

log = logging.getLogger(__name__)


@dataclass
class FrameData:
    frame: np.ndarray
    timestamp: float
    source: str


class CameraManager:
    def __init__(self, config: Config):
        self.config = config
        self.is_webcam_active = False
        self.is_phone_active = False
        self._webcap: Optional[cv2.VideoCapture] = None
        self._running = False

    async def start(self):
        self._running = True
        await self._start_webcam()
        log.info("Cameras started: webcam=%s", "✓" if self.is_webcam_active else "✗")

    async def _start_webcam(self):
        try:
            self._webcap = cv2.VideoCapture(self.config.cameras.webcam_index)
            self._webcap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            self.is_webcam_active = self._webcap.isOpened()
        except Exception as e:
            log.error("Webcam init failed: %s", e)

    async def get_frame_pair(self, timeout: float = 1.0):
        """Get frames from both cameras."""
        if not self.is_webcam_active or self._webcap is None:
            return (None, None)
        
        try:
            ret, frame = await asyncio.get_event_loop().run_in_executor(
                None, self._webcap.read
            )
            if ret:
                fd = FrameData(frame=frame, timestamp=asyncio.get_event_loop().time(), source="webcam")
                return (fd, None)  # Phone not implemented yet
        except Exception as e:
            log.error("Frame capture error: %s", e)
        
        return (None, None)

    async def release(self):
        self._running = False
        if self._webcap:
            self._webcap.release()
        self.is_webcam_active = False
