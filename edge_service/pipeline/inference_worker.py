import time
import threading

class InferenceWorker:

    def __init__(self, buffer, model):

        self.buffer = buffer
        self.model = model
        self.running = False

    def start(self):

        self.running = True

        threading.Thread(
            target=self.loop,
            daemon=True
        ).start()

    def loop(self):

        while self.running:

            frame = self.buffer.latest()

            if frame is None:
                time.sleep(0.01)
                continue

            results = self.model(frame)

            # тут можно отправлять результаты дальше