import threading
import time


class CaptureWorker:

    def __init__(self, driver, buffer, fps=30):

        self.driver = driver
        self.buffer = buffer
        self.fps = fps

        self.running = False

    def start(self):

        self.running = True

        threading.Thread(
            target=self.loop,
            daemon=True
        ).start()

    def loop(self):

        delay = 1 / self.fps

        while self.running:

            frame = self.driver.read_frame()

            self.buffer.write(frame)

            time.sleep(delay)