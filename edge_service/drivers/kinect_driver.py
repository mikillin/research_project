import freenect
import cv2
from .base_driver import BaseCameraDriver


class FreenectDriver(BaseCameraDriver):

    def __init__(self, settings):
        self.settings = settings

    def open(self):
        pass

    def close(self):
        pass

    def read_frame(self):
        frame, _ = freenect.sync_get_video()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame