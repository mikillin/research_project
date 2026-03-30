"""Camera manager service for handling multiple cameras."""

from typing import Dict, Optional, Type
import logging

from camera_service.cameras.base import BaseCamera, CameraConfig
from camera_service.cameras.webcam import WebcamCamera
from camera_service.cameras.kinect360 import Kinect360Camera
from shared.models import CameraType, CameraFrame

logger = logging.getLogger(__name__)


class CameraRegistry:
    """Registry for camera implementations."""

    _cameras: Dict[CameraType, Type[BaseCamera]] = {
        CameraType.WEBCAM: WebcamCamera,
        CameraType.KINECT360: Kinect360Camera,
    }

    @classmethod
    def register(cls, camera_type: CameraType, camera_class: Type[BaseCamera]) -> None:
        """Register a new camera implementation."""
        cls._cameras[camera_type] = camera_class
        logger.info(f"Registered camera type: {camera_type.value}")

    @classmethod
    def get(cls, camera_type: CameraType) -> Optional[Type[BaseCamera]]:
        """Get camera class by type."""
        return cls._cameras.get(camera_type)

    @classmethod
    def available_types(cls) -> list[CameraType]:
        """List all registered camera types."""
        return list(cls._cameras.keys())


class CameraManager:
    """Manages multiple camera instances."""

    def __init__(self):
        self._cameras: Dict[str, BaseCamera] = {}

    def add_camera(self, camera_type: CameraType, config: CameraConfig) -> bool:
        """Add and connect a new camera."""
        if config.camera_id in self._cameras:
            logger.warning(f"Camera {config.camera_id} already exists")
            return False

        camera_class = CameraRegistry.get(camera_type)
        if camera_class is None:
            logger.error(f"Unknown camera type: {camera_type}")
            return False

        camera = camera_class(config)

        if not camera.connect():
            logger.error(f"Failed to connect camera {config.camera_id}")
            return False

        self._cameras[config.camera_id] = camera
        logger.info(f"Added camera: {config.camera_id} ({camera_type.value})")
        return True

    def remove_camera(self, camera_id: str) -> bool:
        """Disconnect and remove a camera."""
        camera = self._cameras.pop(camera_id, None)
        if camera is None:
            return False

        camera.disconnect()
        logger.info(f"Removed camera: {camera_id}")
        return True

    def get_camera(self, camera_id: str) -> Optional[BaseCamera]:
        """Get a camera by ID."""
        return self._cameras.get(camera_id)

    def capture_frame(self, camera_id: str) -> Optional[CameraFrame]:
        """Capture a frame from a specific camera."""
        camera = self._cameras.get(camera_id)
        if camera is None:
            logger.warning(f"Camera not found: {camera_id}")
            return None

        return camera.capture_frame()

    def list_cameras(self) -> list[dict]:
        """List all cameras and their status."""
        return [camera.get_info() for camera in self._cameras.values()]

    def shutdown(self) -> None:
        """Disconnect all cameras."""
        for camera_id in list(self._cameras.keys()):
            self.remove_camera(camera_id)
        logger.info("Camera manager shut down")
