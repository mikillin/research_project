import cv2
from .base_driver import BaseCameraDriver


class OpenCVDriver(BaseCameraDriver):

    def __init__(self, settings):
        self.settings = settings
        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(self.settings.device_index)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.settings.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.settings.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.settings.fps)

        if not self.cap.isOpened():
            raise RuntimeError("OpenCV camera open failed")

    def close(self):
        if self.cap:
            self.cap.release()

    def read_frame(self):
        ok, frame = self.cap.read()
        if not ok:
            raise RuntimeError("Frame read failed")
        return frame