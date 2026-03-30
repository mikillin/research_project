"""Kinect 360 implementation using freenect library."""

import numpy as np
from datetime import datetime
from typing import Optional
import logging
import cv2

from .base import BaseCamera, CameraConfig
from shared.models import CameraType, CameraFrame

logger = logging.getLogger(__name__)

# Kinect support is optional
try:
    import freenect
    KINECT_AVAILABLE = True
except ImportError:
    KINECT_AVAILABLE = False
    logger.warning("freenect not available - Kinect support disabled")


class Kinect360Camera(BaseCamera):
    """Kinect 360 implementation with RGB and depth capture."""

    def __init__(self, config: CameraConfig):
        super().__init__(config)
        self._context = None
        self._device = None

    @property
    def camera_type(self) -> CameraType:
        return CameraType.KINECT360

    def connect(self) -> bool:
        if not KINECT_AVAILABLE:
            logger.error("freenect library not installed")
            return False

        try:
            # Test connection by getting a frame
            frame, _ = freenect.sync_get_video(self.config.device_index)
            if frame is None:
                logger.error(f"Failed to connect to Kinect at index {self.config.device_index}")
                return False

            self._is_running = True
            logger.info(f"Kinect {self.config.camera_id} connected successfully")
            return True

        except Exception as e:
            logger.error(f"Error connecting to Kinect: {e}")
            return False

    def disconnect(self) -> None:
        if KINECT_AVAILABLE:
            freenect.sync_stop()
        self._is_running = False
        logger.info(f"Kinect {self.config.camera_id} disconnected")

    def capture_frame(self) -> Optional[CameraFrame]:
        if not KINECT_AVAILABLE or not self._is_running:
            return None

        try:
            # Capture RGB frame
            rgb_frame, _ = freenect.sync_get_video(self.config.device_index)
            if rgb_frame is None:
                return None

            # Convert from RGB to BGR for OpenCV compatibility
            bgr_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

            # Resize if needed
            if bgr_frame.shape[1] != self.config.width or bgr_frame.shape[0] != self.config.height:
                bgr_frame = cv2.resize(bgr_frame, (self.config.width, self.config.height))

            # Capture depth frame
            depth_frame, _ = freenect.sync_get_depth(self.config.device_index)
            depth_bytes = None

            if depth_frame is not None:
                # Normalize depth to 8-bit for encoding
                depth_normalized = (depth_frame / depth_frame.max() * 255).astype(np.uint8)
                _, depth_buffer = cv2.imencode(".png", depth_normalized)
                depth_bytes = depth_buffer.tobytes()

            # Encode RGB frame
            _, buffer = cv2.imencode(".jpg", bgr_frame, [cv2.IMWRITE_JPEG_QUALITY, 90])

            return CameraFrame(
                camera_id=self.config.camera_id,
                camera_type=self.camera_type,
                frame_data=buffer.tobytes(),
                timestamp=datetime.utcnow(),
                width=bgr_frame.shape[1],
                height=bgr_frame.shape[0],
                depth_frame=depth_bytes,
            )

        except Exception as e:
            logger.error(f"Error capturing Kinect frame: {e}")
            return None

    def is_connected(self) -> bool:
        return self._is_running and KINECT_AVAILABLE

    def get_depth_at_point(self, x: int, y: int) -> Optional[float]:
        """Get depth value at a specific point (in millimeters)."""
        if not KINECT_AVAILABLE or not self._is_running:
            return None

        try:
            depth_frame, _ = freenect.sync_get_depth(self.config.device_index)
            if depth_frame is not None and 0 <= x < depth_frame.shape[1] and 0 <= y < depth_frame.shape[0]:
                return float(depth_frame[y, x])
        except Exception:
            pass

        return None
