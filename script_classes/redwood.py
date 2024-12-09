import os
from dataclasses import dataclass
import cv2
import numpy
import pyautogui

from http_plugin.inventory import Inventory
from http_plugin.stats import Stats
from http_plugin.stats import WOODCUTTING as WOODCUTTING_IDX
from script_random import rsleep
from script_utils import (
    display_debug_screenshot,
    drop_all,
    get_closest_rectangle_to_center,
    get_image_on_screen,
    get_inventory_slots,
    get_screenshot_bgr,
)

from auto_gui import slow_click_in_rect, random_point_near_center_of_rect, slow_click
from settings import WOODCUTTING_DROP_ORDER
from .base import ScriptBase


class CONFIG:
    # Size of entire monitor
    MONITOR_SIZE = {"width": 1727, "height": 1116}
    # Size of game window
    # Includes title bar because it makes clicking more straight forward.
    GAME_WINDOW = {"top": 0, "left": 0, "width": 764, "height": 800}
    TOP_LEFT_WINDOW = {"top": 0, "left": 0, "width": 120, "height": 120}
    DEBUG_SCREENSHOT_SIZE = (500, 500)
    DEBUG_SCREENSHOT_LOCATION = {"top": 0, "left": MONITOR_SIZE["width"] - DEBUG_SCREENSHOT_SIZE[0]}


YELLOW = numpy.array([255, 255, 0])
WOODCUTTING = cv2.imread("pics/woodcutting.png", cv2.IMREAD_COLOR)
SPECIAL = cv2.imread("pics/redwood_special_attack.png", cv2.IMREAD_COLOR)

"""
python3.10 new_main.py --script Redwood -d 10000

Entity Hider - hide local player 2d
Object Marker 4 border
stretch off
Woodcutting:
 - Respawn timers off
 - Redwood icon off
 - Session stats ON

Look west
Reset zoom to 300
"""


@dataclass
class Redwood(ScriptBase):
    sleep_seconds: int = 0.1

    def on_start(self):
        self.last_log = ""
        self.inv = Inventory()
        self.stats = Stats()

        self.inv_slots = get_inventory_slots(CONFIG.GAME_WINDOW)
        print(self.inv_slots)

        self.clicked = 0
        self.log("Starting Script...")

    def on_stop(self):
        self.log("Stopping Script...")

    def on_loop(self):
        if not self.is_woodcutting():
            self.log("stopped chopping")

            if self.clicked >= 4:
                print("Couldn't find a tree to cut")
                exit()

            if self.inv.is_full():
                print("Inventory full, dropping")
                drop_all(WOODCUTTING_DROP_ORDER, time_to_move=(0.10, 0.005))

            # boosted_level, _ = self.stats.level(WOODCUTTING_IDX)
            # if boosted_level < 90:
            if self.try_to_click(SPECIAL):
                print("Using special")
                rsleep(0.5)

            self.click_color(YELLOW)
            self.clicked += 1
        else:
            self.log("still chopping")
            self.clicked = 0

    def on_sleep(self):
        rsleep(10)

    def is_woodcutting(self):
        screenshot = get_screenshot_bgr(CONFIG.TOP_LEFT_WINDOW)
        tl, br = get_image_on_screen(screenshot, WOODCUTTING, threshold=0.65)
        return tl

    def click_color(self, color):
        self.log(f"clicking {color}")
        try:
            rect = get_closest_rectangle_to_center(YELLOW)
        # Failed to find color.
        # Move mouse out of the way and try again.
        except TypeError:
            pyautogui.moveTo(100, 100)
            rect = get_closest_rectangle_to_center(YELLOW)
        if not rect:
            print("Couldn't find a tree")
            return
        slow_click_in_rect(*rect)

    def debug_display(self, img, name="Debug"):
        display_debug_screenshot(
            img,
            CONFIG.DEBUG_SCREENSHOT_LOCATION["top"],
            CONFIG.DEBUG_SCREENSHOT_LOCATION["left"],
            refresh_rate_ms=self.sleep_seconds * 900,
            name=name,
            size=CONFIG.DEBUG_SCREENSHOT_SIZE,
        )

    def try_to_click(self, img, threshold=0.85):
        screenshot = get_screenshot_bgr(CONFIG.GAME_WINDOW)
        tl, br = get_image_on_screen(screenshot, img, threshold)
        if tl:
            slow_click_in_rect(tl, br)
            return True
        else:
            print(f"couldn't find image")
            return False

    def alert(self):
        os.system("afplay /System/Library/Sounds/Sosumi.aiff")
        os.system("afplay /System/Library/Sounds/Sosumi.aiff")
        os.system("afplay /System/Library/Sounds/Sosumi.aiff")

    def log(self, msg):
        if self.last_log != msg:
            print(msg)
            self.last_log = msg
