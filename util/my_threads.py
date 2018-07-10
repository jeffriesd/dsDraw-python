import threading
from time import sleep


class TestThread(threading.Thread):
    """Simple thread class created with added
        stop/start functionality"""

    def __init__(self, target=None, sleep_time=1):
        super().__init__()
        self.running = False
        self.target = target
        self.sleep_time = sleep_time

    def run(self):
        self.running = True
        while self.running:
            self.target()
            sleep(self.sleep_time)

    def stop(self):
        self.running = False

