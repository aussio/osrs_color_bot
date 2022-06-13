from script_random import rsleep
from .base import ScriptBase


class NMZ(ScriptBase):
    def on_loop(self):
        print(f"Loop count: {self.loop_count}")

    def on_sleep(self):
        rsleep(5)
