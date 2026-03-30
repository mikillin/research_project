"""Shared data models used across all services."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import uuid


class CameraType(str, Enum):
    WEBCAM = "webcam"
    KINECT360 = "kinect360"


class DetectorType(str, Enum):
    YOLOV8 = "yolov8"
    YOLOV5 = "yolov5"


@dataclass
class BoundingBox:
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min

    @property
    def center(self) -> tuple[float, float]:
        return (self.x_min + self.width / 2, self.y_min + self.height / 2)

    def to_dict(self) -> dict:
        return {
            "x_min": self.x_min,
            "y_min": self.y_min,
            "x_max": self.x_max,
            "y_max": self.y_max,
            "width": self.width,
            "height": self.height,
        }


@dataclass
class DetectedObject:
    class_id: int
    class_name: str
    confidence: float
    bounding_box: BoundingBox
    object_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> dict:
        return {
            "object_id": self.object_id,
            "class_id": self.class_id,
            "class_name": self.class_name,
            "confidence": round(self.confidence, 4),
            "bounding_box": self.bounding_box.to_dict(),
        }


@dataclass
class DetectionResult:
    request_id: str
    camera_id: str
    timestamp: datetime
    detector_type: DetectorType
    objects: list[DetectedObject]
    processing_time_ms: float
    image_width: int
    image_height: int
    depth_data: Optional[dict] = None  # For Kinect depth information

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "camera_id": self.camera_id,
            "timestamp": self.timestamp.isoformat(),
            "detector_type": self.detector_type.value,
            "objects": [obj.to_dict() for obj in self.objects],
            "object_count": len(self.objects),
            "processing_time_ms": round(self.processing_time_ms, 2),
            "image_dimensions": {
                "width": self.image_width,
                "height": self.image_height,
            },
            "depth_data": self.depth_data,
        }


@dataclass
class CameraFrame:
    camera_id: str
    camera_type: CameraType
    frame_data: bytes
    timestamp: datetime
    width: int
    height: int
    depth_frame: Optional[bytes] = None  # For Kinect

    def to_dict(self) -> dict:
        return {
            "camera_id": self.camera_id,
            "camera_type": self.camera_type.value,
            "timestamp": self.timestamp.isoformat(),
            "width": self.width,
            "height": self.height,
            "has_depth": self.depth_frame is not None,
        }
