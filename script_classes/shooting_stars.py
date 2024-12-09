import os
from dataclasses import dataclass
import cv2
import numpy
import pyautogui

from colors import get_mask
from script_random import rsleep
from script_utils import (
    display_debug_screenshot,
    get_image_on_screen,
    get_rectangle,
    get_screenshot,
    get_screenshot_bgr,
)

from auto_gui import slow_click_in_rect, random_point_near_center_of_rect, slow_click
from .base import ScriptBase


class CONFIG:
    # Size of entire monitor
    MONITOR_SIZE = {"width": 1727, "height": 1116}
    # Size of game window
    # Includes title bar because it makes clicking more straight forward.
    GAME_WINDOW = {"top": 0, "left": 0, "width": 1400, "height": 1025}
    TOP_LEFT_WINDOW = {"top": 0, "left": 0, "width": 120, "height": 120}
    # NOT STRETCHED!
    CHAT_WINDOW = {"top": 851, "left": 8, "width": 637, "height": 148}
    DEBUG_SCREENSHOT_SIZE = (500, 500)
    DEBUG_SCREENSHOT_LOCATION = {"top": 0, "left": MONITOR_SIZE["width"] - DEBUG_SCREENSHOT_SIZE[0]}


MAGENTA = numpy.array([255, 0, 255])
MINING = cv2.imread("pics/mining.png", cv2.IMREAD_COLOR)


"""
python3.10 new_main.py --script ShootingStars -n 1

Entity Hider
Screen marker over rock
stretch off
07 on
"""


@dataclass
class ShootingStars(ScriptBase):
    sleep_seconds: int = 0.1

    def on_start(self):
        self.last_log = ""
        self.clicked = 0
        self.log("Starting Script...")

    def on_stop(self):
        self.log("Stopping Script...")

    def on_loop(self):
        if not self.is_mining():
            if self.clicked >= 2:
                print("Star is gone")
                exit()
            self.log("stopped mining")
            self.click_color(MAGENTA)
            self.clicked += 1
        else:
            self.log("still mining")
            self.clicked = 0

    def on_sleep(self):
        rsleep(10)

    def is_mining(self):
        screenshot = get_screenshot_bgr(CONFIG.TOP_LEFT_WINDOW)
        tl, br = get_image_on_screen(screenshot, MINING, threshold=0.65)
        return tl

    def click_color(self, color):
        self.log(f"clicking {color}")
        try:
            screenshot = get_screenshot(CONFIG.GAME_WINDOW)
            tl, br = self.get_color_rect(screenshot, color)
        # Failed to find color.
        # Move mouse out of the way and try again.
        except TypeError:
            pyautogui.moveTo(100, 100)
            screenshot = get_screenshot(CONFIG.GAME_WINDOW)
            tl, br = self.get_color_rect(screenshot, color)
        slow_click_in_rect(tl, br)

    def get_color_rect(self, image, color):
        mask = get_mask(image, color)
        # self.debug_display(mask)
        # rsleep(1)

        # Since this script assums that you are using RS Paint for
        # where to click, then likely there's one area really, but not perfectly 1.
        rect = get_rectangle(mask, color_name=color, only_one=False)
        if rect is None:
            print("No rect of color: {}".format(color))
        return rect

    def debug_display(self, img, name="Debug"):
        display_debug_screenshot(
            img,
            CONFIG.DEBUG_SCREENSHOT_LOCATION["top"],
            CONFIG.DEBUG_SCREENSHOT_LOCATION["left"],
            refresh_rate_ms=self.sleep_seconds * 900,
            name=name,
            size=CONFIG.DEBUG_SCREENSHOT_SIZE,
        )

    def alert(self):
        os.system("afplay /System/Library/Sounds/Sosumi.aiff")
        os.system("afplay /System/Library/Sounds/Sosumi.aiff")
        os.system("afplay /System/Library/Sounds/Sosumi.aiff")

    def log(self, msg):
        if self.last_log != msg:
            print(msg)
            self.last_log = msg
