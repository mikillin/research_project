"""YOLOv5 detector implementation using torch hub."""

import numpy as np
import logging
from typing import Optional
import torch

from .base import BaseDetector, DetectorConfig
from shared.models import DetectedObject, DetectorType, BoundingBox

logger = logging.getLogger(__name__)


class YOLOv5Detector(BaseDetector):
    """YOLOv5 object detector using torch hub."""

    def __init__(self, config: DetectorConfig):
        super().__init__(config)
        self._model = None

    @property
    def detector_type(self) -> DetectorType:
        return DetectorType.YOLOV5

    def load_model(self) -> bool:
        try:
            model_name = self.config.model_path or "yolov5s"
            self._model = torch.hub.load(
                "ultralytics/yolov5",
                model_name,
                pretrained=True,
            )

            # Configure model
            self._model.conf = self.config.confidence_threshold
            self._model.iou = self.config.nms_threshold

            # Set device
            if self.config.device == "cuda" and torch.cuda.is_available():
                self._model = self._model.cuda()
            elif self.config.device == "mps" and torch.backends.mps.is_available():
                self._model = self._model.to("mps")

            self._is_loaded = True
            logger.info(f"YOLOv5 model loaded: {model_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to load YOLOv5 model: {e}")
            return False

    def detect(self, image: np.ndarray) -> list[DetectedObject]:
        if self._model is None:
            logger.warning("Model not loaded")
            return []

        try:
            results = self._model(image, size=self.config.input_size[0])
            predictions = results.pandas().xyxy[0]

            detected_objects = []

            for _, row in predictions.iterrows():
                detected_objects.append(
                    DetectedObject(
                        class_id=int(row["class"]),
                        class_name=row["name"],
                        confidence=float(row["confidence"]),
                        bounding_box=BoundingBox(
                            x_min=float(row["xmin"]),
                            y_min=float(row["ymin"]),
                            x_max=float(row["xmax"]),
                            y_max=float(row["ymax"]),
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
        return self._model.names
