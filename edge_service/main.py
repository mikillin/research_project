from fastapi import FastAPI
from api.camera_routes import router as camera_router

app = FastAPI(title="Kinect REST API")

app.include_router(camera_router)