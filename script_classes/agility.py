import os
from dataclasses import dataclass
import numpy
import pyautogui

from script_random import rsleep
from script_utils import (
    display_debug_screenshot,
    get_screenshot,
    get_rectangle,
)
from colors import get_mask

from auto_gui import slow_click_in_rect, random_point_near_center_of_rect, slow_click
from .base import ScriptBase
import http_plugin.item_ids as item_ids
from http_plugin.inventory import Inventory

class CONFIG:
    # Size of entire monitor
    MONITOR_SIZE = {"width": 1727, "height": 1116}
    # Size of game window
    # Includes title bar because it makes clicking more straight forward.
    GAME_WINDOW = {"top": 0, "left": 0, "width": 1400, "height": 1025}
    # NOT STRETCHED!
    CHAT_WINDOW = {"top": 851, "left": 8, "width": 637, "height": 148}
    DEBUG_SCREENSHOT_SIZE = (500, 500)
    DEBUG_SCREENSHOT_LOCATION = {"top": 0, "left": MONITOR_SIZE["width"] - DEBUG_SCREENSHOT_SIZE[0]}

RED = numpy.array([255, 0, 0])
YELLOW = numpy.array([255, 255, 0])
CYAN = numpy.array([0, 255, 255])
MAGENTA = numpy.array([255, 0, 255])

# Amount of time to sleep each loop.
LAG_FACTOR = 0

"""
python3.10 new_main.py --script PrifSmithing -n 1

look South
Reset zoom to 300
Entity Hider
Line of Sight off
Stretch mode 30%
width 1400

Agility off
Metronome off

height excludes chat tabs
"""
@dataclass
class Agility(ScriptBase):
    sleep_seconds: int = 0.1

    def on_start(self):
        self.last_log = ""

        self.log("Starting Script...")
        self.inv = Inventory()
        self.click_cache_coor = {}

    def on_stop(self):
        self.log("Stopping Script...")

    def on_loop(self):
        # self.debug = copy(self.client)
        # self.debug_display(self.debug)
        self.high_alch()
        rsleep(3, 0.1)

        # self.click_color(MAGENTA)
        # rsleep(5.5, 0)
        # self.click_color(YELLOW)
        # rsleep(5, 0)
        # self.click_color(CYAN)
        # rsleep(7, 0)
        # self.click_color(MAGENTA)
        # rsleep(9.5, 0)
        # self.click_color(RED)
        # rsleep(4, 0)
        # # self.click_color(YELLOW)
        # rsleep(9, 0)
        # self.click_color(MAGENTA)
        # rsleep(5, 0)
        # self.click_color(RED)
        # rsleep(7, 0)
        # alch x2
        pass
        
    def on_sleep(self):
        rsleep(LAG_FACTOR)


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

    def high_alch(self):
        x, y = random_point_near_center_of_rect((1338*2, 871*2), (1361*2, 898*2), absolute=False)
        slow_click(x, y)
        rsleep(0.1)
        slow_click(x, y)

    # Not actually empty, but only hammer and knife
    def inventory_empty(self):
        has_roots = self.inv.has_item(item_ids.BRUMA_ROOT)
        has_kindling = self.inv.has_item(item_ids.BRUMA_KINDLING)
        return not has_roots and not has_kindling

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
        os.system('afplay /System/Library/Sounds/Sosumi.aiff')
        os.system('afplay /System/Library/Sounds/Sosumi.aiff')
        os.system('afplay /System/Library/Sounds/Sosumi.aiff')
    
    def log(self, msg):
        if self.last_log != msg:
            print(msg)
            self.last_log = msg

