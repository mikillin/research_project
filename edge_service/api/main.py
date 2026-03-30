"""Main API gateway that coordinates camera and detection services."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs (configurable via environment)
CAMERA_SERVICE_URL = "[camera_service](http://camera_service:8001)"
DETECTION_SERVICE_URL = "[detection_engine](http://detection_engine:8002)"

http_client: Optional[httpx.AsyncClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    http_client = httpx.AsyncClient(timeout=30.0)
    logger.info("API Gateway started")
    yield
    await http_client.aclose()
    logger.info("API Gateway stopped")


app = FastAPI(
    title="Object Detection API",
    description="Unified API for camera management and object detection",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DetectFromCameraRequest(BaseModel):
    camera_id: str
    detector_id: Optional[str] = None


class DetectFromCameraResponse(BaseModel):
    camera_id: str
    detector_type: str
    objects: list[dict]
    object_count: int
    processing_time_ms: float
    timestamp: str


@app.get("/health")
async def health_check():
    """Check health of all services."""
    camera_health = "unknown"
    detection_health = "unknown"

    try:
        response = await http_client.get(f"{CAMERA_SERVICE_URL}/health")
        camera_health = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception:
        camera_health = "unreachable"

    try:
        response = await http_client.get(f"{DETECTION_SERVICE_URL}/health")
        detection_health = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception:
        detection_health = "unreachable"

    return {
        "status": "healthy",
        "services": {
            "camera": camera_health,
            "detection": detection_health,
        },
    }


# --- Camera endpoints (proxy to camera service) ---

@app.get("/cameras")
async def list_cameras():
    """List all connected cameras."""
    response = await http_client.get(f"{CAMERA_SERVICE_URL}/cameras")
    return response.json()


@app.post("/cameras")
async def add_camera(request: dict):
    """Add a new camera."""
    response = await http_client.post(f"{CAMERA_SERVICE_URL}/cameras", json=request)
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()


@app.delete("/cameras/{camera_id}")
async def remove_camera(camera_id: str):
    """Remove a camera."""
    response = await http_client.delete(f"{CAMERA_SERVICE_URL}/cameras/{camera_id}")
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")
    return response.json()


# --- Detector endpoints (proxy to detection service) ---

@app.get("/detectors")
async def list_detectors():
    """List all loaded detectors."""
    response = await http_client.get(f"{DETECTION_SERVICE_URL}/detectors")
    return response.json()


@app.post("/detectors")
async def add_detector(request: dict):
    """Add a new detector."""
    response = await http_client.post(f"{DETECTION_SERVICE_URL}/detectors", json=request)
    if response.status_code != 201:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()


# --- Detection endpoints ---

@app.post("/detect/camera", response_model=DetectFromCameraResponse)
async def detect_from_camera(request: DetectFromCameraRequest):
    """Capture frame from camera and perform object detection."""
    # Step 1: Capture frame from camera
    capture_response = await http_client.get(
        f"{CAMERA_SERVICE_URL}/cameras/{request.camera_id}/capture"
    )

    if capture_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to capture from camera {request.camera_id}",
        )

    frame_data = capture_response.json()

    # Step 2: Send frame to detection service
    import base64
    frame_bytes = base64.b64decode(frame_data["frame_base64"])

    files = {"file": ("frame.jpg", frame_bytes, "image/jpeg")}
    data = {"camera_id": request.camera_id}

    if request.detector_id:
        data["detector_id"] = request.detector_id

    detection_response = await http_client.post(
        f"{DETECTION_SERVICE_URL}/detect",
        files=files,
        data=data,
    )

    if detection_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Detection failed",
        )

    result = detection_response.json()

    return DetectFromCameraResponse(
        camera_id=result["camera_id"],
        detector_type=result["detector_type"],
        objects=result["objects"],
        object_count=result["object_count"],
        processing_time_ms=result["processing_time_ms"],
        timestamp=result["timestamp"],
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
