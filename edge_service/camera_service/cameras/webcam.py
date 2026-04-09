"""Webcam implementation using OpenCV."""

import cv2
import numpy as np
from datetime import datetime
from typing import Optional
import logging

from .base import BaseCamera, CameraConfig
from shared.models import CameraType, CameraFrame

logger = logging.getLogger(__name__)


class WebcamCamera(BaseCamera):
    """Standard webcam implementation using OpenCV."""

    def __init__(self, config: CameraConfig):
        super().__init__(config)
        self._capture: Optional[cv2.VideoCapture] = None

    @property
    def camera_type(self) -> CameraType:
        return CameraType.WEBCAM

    def connect(self) -> bool:
        try:
            self._capture = cv2.VideoCapture(self.config.device_index)

            if not self._capture.isOpened():
                logger.error(f"Failed to open webcam at index {self.config.device_index}")
                return False

            # Configure camera settings
            self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
            self._capture.set(cv2.CAP_PROP_FPS, self.config.fps)

            self._is_running = True
            logger.info(f"Webcam {self.config.camera_id} connected successfully")
            return True

        except Exception as e:
            logger.error(f"Error connecting to webcam: {e}")
            return False

    def disconnect(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None
        self._is_running = False
        logger.info(f"Webcam {self.config.camera_id} disconnected")

    def capture_frame(self) -> CameraFrame:
        if self._capture is None or not self._capture.isOpened():
            logger.warning("Webcam not connected")
            return None

        ret, frame = self._capture.read()

        if not ret:
            logger.warning("Failed to capture frame from webcam")
            return None

        # Encode frame to bytes
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 90])

        return CameraFrame(
            camera_id=self.config.camera_id,
            camera_type=self.camera_type,
            frame_data=buffer.tobytes(),
            timestamp=datetime.utcnow(),
            width=frame.shape[1],
            height=frame.shape[0],
        )

    def is_connected(self) -> bool:
        return self._capture is not None and self._capture.isOpened()
