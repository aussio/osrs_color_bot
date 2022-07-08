from dataclasses import dataclass
from copy import copy

import numpy
from script_random import rsleep
from script_utils import (
    debug_points_on_screen,
    display_debug_screenshot,
    get_inventory_corner_points,
    get_screenshot_bgr,
)
from .base import ScriptBase

# Should probably end up being moved into a separate file.
class CONFIG:
    MONITOR_SIZE = {"width": 1679, "height": 1049}
    GAME_WINDOW = {"top": 0, "left": 0, "width": 817, "height": MONITOR_SIZE["height"]}
    DEBUG_SCREENSHOT_LOCATION = {"top": 0, "left": MONITOR_SIZE["width"] - GAME_WINDOW["width"]}


class CONSTANTS:
    WINDOW_TITLE_BAR_HEIGHT = 25


@dataclass
class Slayer(ScriptBase):

    # Client screenshot (Mat = Matrix)
    client: numpy.ndarray = None
    # Debug screenshot
    debug: numpy.ndarray = None
    sleep_seconds: int = 0.1

    def on_start(self):
        print("Starting...")

    def on_stop(self):
        print("Stopping...")

    def on_loop(self):
        print(f"Loop count: {self.loop_count}")
        self.client = get_screenshot_bgr(CONFIG.GAME_WINDOW)
        self.debug = copy(self.client)
        tl, tr, bl, br = get_inventory_corner_points(self.client)
        if all([tl, tr, bl, br]):
            debug_points_on_screen(self.debug, [tl, tr, bl, br])
        self.display_debug()

    def on_sleep(self):
        rsleep(self.sleep_seconds)

    def display_debug(self):
        display_debug_screenshot(
            self.debug,
            CONFIG.DEBUG_SCREENSHOT_LOCATION["top"],
            CONFIG.DEBUG_SCREENSHOT_LOCATION["left"],
            refresh_rate_ms=self.sleep_seconds * 900,
        )
