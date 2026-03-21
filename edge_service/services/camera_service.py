import cv2

from core.frame_buffer import FrameBuffer
from pipeline.capture_worker import CaptureWorker
from drivers.opencv_driver import OpenCVDriver


class CameraService:

    def __init__(self):

        self.buffer = FrameBuffer()
        self.driver = None
        self.worker = None
        self.enabled = False

    def enable(self):

        if self.enabled:
            return

        self.driver = OpenCVDriver(None)
        self.driver.open()

        self.worker = CaptureWorker(
            self.driver,
            self.buffer,
            fps=30
        )

        self.worker.start()

        self.enabled = True

    def disable(self):

        if not self.enabled:
            return

        self.worker.stop()
        self.driver.close()

        self.enabled = False

    def get_frame(self):

        frame = self.buffer.read()

        if frame is None:
            raise RuntimeError("no frame")

        ok, jpg = cv2.imencode(".jpg", frame)

        if not ok:
            raise RuntimeError("jpeg failed")

        return jpg.tobytes()