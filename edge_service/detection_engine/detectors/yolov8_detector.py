"""YOLOv8 detector implementation using ultralytics."""

import numpy as np
import logging
from typing import Optional

from .base import BaseDetector, DetectorConfig
from shared.models import DetectedObject, DetectorType, BoundingBox

logger = logging.getLogger(__name__)

try:
    from ultralytics import YOLO
    YOLOV8_AVAILABLE = True
except ImportError:
    YOLOV8_AVAILABLE = False
    logger.warning("ultralytics not installed - YOLOv8 unavailable")


class YOLOv8Detector(BaseDetector):
    """YOLOv8 object detector."""

    def __init__(self, config: DetectorConfig):
        super().__init__(config)
        self._model: Optional[YOLO] = None

    @property
    def detector_type(self) -> DetectorType:
        return DetectorType.YOLOV8

    def load_model(self) -> bool:
        if not YOLOV8_AVAILABLE:
            logger.error("ultralytics library not installed")
            return False

        try:
            model_path = self.config.model_path or "yolov8n.pt"
            self._model = YOLO(model_path)

            # Set device
            if self.config.device == "cuda":
                self._model.to("cuda")
            elif self.config.device == "mps":
                self._model.to("mps")

            self._is_loaded = True
            logger.info(f"YOLOv8 model loaded: {model_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load YOLOv8 model: {e}")
            return False

    def detect(self, image: np.ndarray) -> list[DetectedObject]:
        if self._model is None:
            logger.warning("Model not loaded")
            return []

        try:
            results = self._model(
                image,
                conf=self.config.confidence_threshold,
                iou=self.config.nms_threshold,
                imgsz=self.config.input_size[0],
                verbose=False,
            )

            detected_objects = []

            for result in results:
                boxes = result.boxes

                if boxes is None:
                    continue

                for i in range(len(boxes)):
                    xyxy = boxes.xyxy[i].cpu().numpy()
                    conf = float(boxes.conf[i].cpu().numpy())
                    cls_id = int(boxes.cls[i].cpu().numpy())
                    cls_name = self._model.names[cls_id]

                    detected_objects.append(
                        DetectedObject(
                            class_id=cls_id,
                            class_name=cls_name,
                            confidence=conf,
                            bounding_box=BoundingBox(
                                x_min=float(xyxy[0]),
                                y_min=float(xyxy[1]),
                                x_max=float(xyxy[2]),
                                y_max=float(xyxy[3]),
                            ),
                        )
                    )

            return detected_objects

        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []

    def get_class_names(self) -> list[str]:
        if self._model is None:
            return []
        return list(self._model.names.values())
