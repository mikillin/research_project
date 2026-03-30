"""Camera service FastAPI application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import base64
import logging

from camera_service.services.camera_manager import CameraManager, CameraRegistry
from camera_service.cameras.base import CameraConfig
from shared.models import CameraType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

camera_manager = CameraManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting camera service...")
    yield
    logger.info("Shutting down camera service...")
    camera_manager.shutdown()


app = FastAPI(
    title="Camera Service",
    description="Service for managing multiple camera sources",
    version="1.0.0",
    lifespan=lifespan,
)


class AddCameraRequest(BaseModel):
    camera_id: str
    camera_type: CameraType
    device_index: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30


class CaptureResponse(BaseModel):
    camera_id: str
    camera_type: str
    timestamp: str
    width: int
    height: int
    frame_base64: str
    depth_frame_base64: str | None = None


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "camera"}


@app.get("/cameras")
async def list_cameras():
    """List all connected cameras."""
    return {"cameras": camera_manager.list_cameras()}


@app.get("/cameras/types")
async def list_camera_types():
    """List available camera types."""
    return {"types": [t.value for t in CameraRegistry.available_types()]}


@app.post("/cameras", status_code=status.HTTP_201_CREATED)
async def add_camera(request: AddCameraRequest):
    """Add and connect a new camera."""
    config = CameraConfig(
        camera_id=request.camera_id,
        device_index=request.device_index,
        width=request.width,
        height=request.height,
        fps=request.fps,
    )

    success = camera_manager.add_camera(request.camera_type, config)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add camera {request.camera_id}",
        )

    return {"message": f"Camera {request.camera_id} added successfully"}


@app.delete("/cameras/{camera_id}")
async def remove_camera(camera_id: str):
    """Remove a camera."""
    success = camera_manager.remove_camera(camera_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera {camera_id} not found",
        )

    return {"message": f"Camera {camera_id} removed"}


@app.get("/cameras/{camera_id}/capture", response_model=CaptureResponse)
async def capture_frame(camera_id: str):
    """Capture a single frame from a camera."""
    frame = camera_manager.capture_frame(camera_id)

    if frame is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to capture frame from camera {camera_id}",
        )

    return CaptureResponse(
        camera_id=frame.camera_id,
        camera_type=frame.camera_type.value,
        timestamp=frame.timestamp.isoformat(),
        width=frame.width,
        height=frame.height,
        frame_base64=base64.b64encode(frame.frame_data).decode(),
        depth_frame_base64=base64.b64encode(frame.depth_frame).decode() if frame.depth_frame else None,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
