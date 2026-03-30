"""Detection service for managing detectors."""

from typing import Dict, Optional, Type
import numpy as np
import cv2
import time
import uuid
from datetime import datetime
import logging

from detection_engine.detectors.base import BaseDetector, DetectorConfig
from detection_engine.detectors.yolov8_detector import YOLOv8Detector
from detection_engine.detectors.yolov5_detector import YOLOv5Detector
from shared.models import DetectorType, DetectionResult, CameraFrame

logger = logging.getLogger(__name__)


class DetectorRegistry:
    """Registry for detector implementations."""

    _detectors: Dict[DetectorType, Type[BaseDetector]] = {
        DetectorType.YOLOV8: YOLOv8Detector,
        DetectorType.YOLOV5: YOLOv5Detector,
    }

    @classmethod
    def register(cls, detector_type: DetectorType, detector_class: Type[BaseDetector]) -> None:
        """Register a new detector implementation."""
        cls._detectors[detector_type] = detector_class
        logger.info(f"Registered detector type: {detector_type.value}")

    @classmethod
    def get(cls, detector_type: DetectorType) -> Optional[Type[BaseDetector]]:
        """Get detector class by type."""
        return cls._detectors.get(detector_type)

    @classmethod
    def available_types(cls) -> list[DetectorType]:
        """List all registered detector types."""
        return list(cls._detectors.keys())


class DetectionService:
    """Service for performing object detection."""

    def __init__(self):
        self._detectors: Dict[str, BaseDetector] = {}
        self._default_detector_id: Optional[str] = None

    def add_detector(
        self,
        detector_id: str,
        detector_type: DetectorType,
        config: Optional[DetectorConfig] = None,
    ) -> bool:
        """Add and load a new detector."""
        if detector_id in self._detectors:
            logger.warning(f"Detector {detector_id} already exists")
            return False

        detector_class = DetectorRegistry.get(detector_type)
        if detector_class is None:
            logger.error(f"Unknown detector type: {detector_type}")
            return False

        config = config or DetectorConfig()
        detector = detector_class(config)

        if not detector.load_model():
            logger.error(f"Failed to load detector {detector_id}")
            return False

        self._detectors[detector_id] = detector

        # Set as default if first detector
        if self._default_detector_id is None:
            self._default_detector_id = detector_id

        logger.info(f"Added detector: {detector_id} ({detector_type.value})")
        return True

    def remove_detector(self, detector_id: str) -> bool:
        """Remove a detector."""
        if detector_id not in self._detectors:
            return False

        del self._detectors[detector_id]

        if self._default_detector_id == detector_id:
            self._default_detector_id = next(iter(self._detectors), None)

        logger.info(f"Removed detector: {detector_id}")
        return True

    def detect_from_frame(
        self,
        frame: CameraFrame,
        detector_id: Optional[str] = None,
    ) -> Optional[DetectionResult]:
        """Perform detection on a camera frame."""
        # Decode frame
        nparr = np.frombuffer(frame.frame_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            logger.error("Failed to decode frame")
            return None

        return self.detect_from_image(
            image=image,
            camera_id=frame.camera_id,
            detector_id=detector_id,
            depth_data=self._extract_depth_data(frame) if frame.depth_frame else None,
        )

    def detect_from_image(
        self,
        image: np.ndarray,
        camera_id: str = "unknown",
        detector_id: Optional[str] = None,
        depth_data: Optional[dict] = None,
    ) -> Optional[DetectionResult]:
        """Perform detection on a numpy image."""
        detector_id = detector_id or self._default_detector_id

        if detector_id is None:
            logger.error("No detector available")
            return None

        detector = self._detectors.get(detector_id)
        if detector is None:
            logger.error(f"Detector not found: {detector_id}")
            return None

        start_time = time.perf_counter()
        detected_objects = detector.detect(image)
        processing_time = (time.perf_counter() - start_time) * 1000

        return DetectionResult(
            request_id=str(uuid.uuid4()),
            camera_id=camera_id,
            timestamp=datetime.utcnow(),
            detector_type=detector.detector_type,
            objects=detected_objects,
            processing_time_ms=processing_time,
            image_width=image.shape[1],
            image_height=image.shape[0],
            depth_data=depth_data,
        )

    def _extract_depth_data(self, frame: CameraFrame) -> Optional[dict]:
        """Extract depth information from a Kinect frame."""
        if frame.depth_frame is None:
            return None

        try:
            nparr = np.frombuffer(frame.depth_frame, np.uint8)
            depth_image = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)

            if depth_image is None:
                return None

            return {
                "min_depth": float(depth_image.min()),
                "max_depth": float(depth_image.max()),
                "mean_depth": float(depth_image.mean()),
            }

        except Exception as e:
            logger.error(f"Error extracting depth data: {e}")
            return None

    def list_detectors(self) -> list[dict]:
        """List all detectors and their status."""
        return [
            {"detector_id": did, **detector.get_info()}
            for did, detector in self._detectors.items()
        ]

    def get_class_names(self, detector_id: Optional[str] = None) -> list[str]:
        """Get class names for a detector."""
        detector_id = detector_id or self._default_detector_id
        if detector_id is None:
            return []

        detector = self._detectors.get(detector_id)
        if detector is None:
            return []

        return detector.get_class_names()
