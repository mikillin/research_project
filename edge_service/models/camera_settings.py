from pydantic import BaseModel


class CameraSettings(BaseModel):
    width: int = 640
    height: int = 480
    fps: int = 30
    device_index: int = 0