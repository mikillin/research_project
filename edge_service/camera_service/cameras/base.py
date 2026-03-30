"""Abstract base class for camera implementations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import numpy as np

from shared.models import CameraType, CameraFrame


@dataclass
class CameraConfig:
    camera_id: str
    width: int = 640
    height: int = 480
    fps: int = 30
    device_index: int = 0


class BaseCamera(ABC):
    """Base class for all camera implementations."""

    def __init__(self, config: CameraConfig):
        self.config = config
        self._is_running = False

    @property
    @abstractmethod
    def camera_type(self) -> CameraType:
        """Return the type of camera."""
        pass

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the camera."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the camera."""
        pass

    @abstractmethod
    def capture_frame(self) -> Optional[CameraFrame]:
        """Capture a single frame from the camera."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if camera is connected and operational."""
        pass

    def get_info(self) -> dict:
        """Return camera information."""
        return {
            "camera_id": self.config.camera_id,
            "camera_type": self.camera_type.value,
            "resolution": f"{self.config.width}x{self.config.height}",
            "fps": self.config.fps,
            "is_connected": self.is_connected(),
        }
