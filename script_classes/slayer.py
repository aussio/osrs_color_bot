from script_random import rsleep
from .base import ScriptBase


class Slayer(ScriptBase):
    def on_start(self):
        print("Starting...")

    def on_stop(self):
        print("Stopping...")

    def on_loop(self):
        print(f"Loop count: {self.loop_count}")

    def on_sleep(self):
        rsleep(5)
