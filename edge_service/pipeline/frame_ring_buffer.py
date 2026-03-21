import threading


class FrameRingBuffer:

    def __init__(self, size=10):
        self.size = size
        self.frames = [None] * size
        self.index = 0
        self.lock = threading.Lock()

    def write(self, frame):

        with self.lock:
            self.frames[self.index] = frame
            self.index = (self.index + 1) % self.size

    def latest(self):

        with self.lock:
            idx = (self.index - 1) % self.size
            return self.frames[idx]