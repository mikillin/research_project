"""Abstract base class for object detection implementations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import numpy as np

from shared.models import DetectedObject, DetectorType


@dataclass
class DetectorConfig:
    model_path: Optional[str] = None
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.4
    device: str = "cpu"  # "cpu", "cuda", "mps"
    input_size: tuple[int, int] = (640, 640)


class BaseDetector(ABC):
    """Base class for all detector implementations."""

    def __init__(self, config: DetectorConfig):
        self.config = config
        self._is_loaded = False

    @property
    @abstractmethod
    def detector_type(self) -> DetectorType:
        """Return the detector type."""
        pass

    @abstractmethod
    def load_model(self) -> bool:
        """Load the detection model."""
        pass

    @abstractmethod
    def detect(self, image: np.ndarray) -> list[DetectedObject]:
        """Perform object detection on an image."""
        pass

    @abstractmethod
    def get_class_names(self) -> list[str]:
        """Get list of detectable class names."""
        pass

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_loaded

    def get_info(self) -> dict:
        """Return detector information."""
        return {
            "detector_type": self.detector_type.value,
            "is_loaded": self.is_loaded(),
            "confidence_threshold": self.config.confidence_threshold,
            "device": self.config.device,
            "input_size": self.config.input_size,
        }
