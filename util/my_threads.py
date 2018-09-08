import threading
from time import sleep


class TestThread(threading.Thread):
    """Simple thread class created with added
        stop/start functionality"""

    def __init__(self, target, sleep_time=1):
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


class CommandThread(threading.Thread):

    def __init__(self, target, text, caller):
        super().__init__()
        self.target = target
        self.text = text
        self.caller = caller

    def run(self):
        try:
            self.target()
        except Exception as e:
            self.caller.raise_cmd_ex(e, self.text)


class GraphSimThread(threading.Thread):

    def __init__(self, n_iter, render):
        super().__init__()
        self.n_iter = n_iter
        self.render = render

    def run(self):
        self.render.simulating = True
        for i in range(self.n_iter):
            self.render.move_nodes()
            self.render.display(do_render=False)
        self.render.simulating = False



