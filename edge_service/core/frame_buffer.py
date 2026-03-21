import threading


class FrameBuffer:

    def __init__(self):
        self.lock = threading.Lock()
        self.frame = None
        self.timestamp = None

    def write(self, frame):

        with self.lock:
            self.frame = frame

    def read(self):

        with self.lock:
            return self.frame