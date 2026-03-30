"""Detection engine FastAPI application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel
from typing import Optional
import numpy as np
import cv2
import logging

from detection_engine.services.detection_service import DetectionService, DetectorRegistry
from detection_engine.detectors.base import DetectorConfig
from shared.models import DetectorType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

detection_service = DetectionService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting detection engine...")
    # Load default detector
    detection_service.add_detector(
        detector_id="default",
        detector_type=DetectorType.YOLOV8,
        config=DetectorConfig(confidence_threshold=0.5),
    )
    yield
    logger.info("Shutting down detection engine...")


app = FastAPI(
    title="Detection Engine",
    description="Object detection service using YOLO models",
    version="1.0.0",
    lifespan=lifespan,
)


class AddDetectorRequest(BaseModel):
    detector_id: str
    detector_type: DetectorType
    model_path: Optional[str] = None
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.4
    device: str = "cpu"


class DetectionResponse(BaseModel):
    request_id: str
    camera_id: str
    timestamp: str
    detector_type: str
    objects: list[dict]
    object_count: int
    processing_time_ms: float
    image_dimensions: dict
    depth_data: Optional[dict] = None


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "detection_engine"}


@app.get("/detectors")
async def list_detectors():
    """List all loaded detectors."""
    return {"detectors": detection_service.list_detectors()}


@app.get("/detectors/types")
async def list_detector_types():
    """List available detector types."""
    return {"types": [t.value for t in DetectorRegistry.available_types()]}


@app.post("/detectors", status_code=status.HTTP_201_CREATED)
async def add_detector(request: AddDetectorRequest):
    """Add and load a new detector."""
    config = DetectorConfig(
        model_path=request.model_path,
        confidence_threshold=request.confidence_threshold,
        nms_threshold=request.nms_threshold,
        device=request.device,
    )

    success = detection_service.add_detector(
        detector_id=request.detector_id,
        detector_type=request.detector_type,
        config=config,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add detector {request.detector_id}",
        )

    return {"message": f"Detector {request.detector_id} added successfully"}


@app.delete("/detectors/{detector_id}")
async def remove_detector(detector_id: str):
    """Remove a detector."""
    success = detection_service.remove_detector(detector_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detector {detector_id} not found",
        )

    return {"message": f"Detector {detector_id} removed"}


@app.get("/detectors/{detector_id}/classes")
async def get_class_names(detector_id: str):
    """Get detectable class names for a detector."""
    classes = detection_service.get_class_names(detector_id)

    if not classes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detector {detector_id} not found or has no classes",
        )

    return {"detector_id": detector_id, "classes": classes}


@app.post("/detect", response_model=DetectionResponse)
async def detect_objects(
    file: UploadFile = File(...),
    detector_id: Optional[str] = Form(None),
    camera_id: str = Form("upload"),
):
    """Perform object detection on an uploaded image."""
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if image is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file",
        )

    result = detection_service.detect_from_image(
        image=image,
        camera_id=camera_id,
        detector_id=detector_id,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Detection failed",
        )

    return DetectionResponse(**result.to_dict())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
