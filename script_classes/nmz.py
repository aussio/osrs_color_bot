import pyautogui
import cv2
from dataclasses import dataclass
from copy import copy

from script_random import rsleep, random_near_point
from script_utils import (
    display_debug_screenshot,
    get_inventory_corner_points,
    get_screenshot_bgr,
    calculate_inventory_slots,
    get_image_on_screen,
)

from auto_gui import click, press_key

from settings import CLEAN_CLICK_ORDER
from .base import ScriptBase

class CONFIG:
    MONITOR_SIZE = {"width": 1679, "height": 1049}
    GAME_WINDOW = {"top": 0, "left": 0, "width": 769, "height": MONITOR_SIZE["height"]}
    DEBUG_SCREENSHOT_LOCATION = {"top": 0, "left": MONITOR_SIZE["width"] - GAME_WINDOW["width"]}
    AMULET_WINDOW = {"top": 65, "left": 0, "width": 120, "height": 120}

@dataclass
class NMZ(ScriptBase):
    # Slices used for partial screenshot matching
    inventory_slices: tuple[slice] = None
    inventory_slots: list = None
    
    sleep_seconds: int = 0.1

    def on_start(self):
        print("Starting...")
        self.client = get_screenshot_bgr(CONFIG.GAME_WINDOW)
        self.debug = copy(self.client)
        self.set_inventory_slice()

    def on_stop(self):
        print("Stopping...")

    def on_loop(self):
        print(f"Loop count: {self.loop_count}")
        # if self.inventory_slices:
            # inv_shot = self.debug[self.inventory_slices[0], self.inventory_slices[1]]
        has_amulet = self.is_amulet_equipped()
        print("is amulet equipped?", has_amulet)
        if has_amulet:
            click(*self.inventory_slots[0])
            click(*self.inventory_slots[1])
            press_key("space", hold=1.25)
            rsleep(10)
        
            


    def on_sleep(self):
        rsleep(1)

    def debug_display(self, img, name="Debug"):
        display_debug_screenshot(
            img,
            CONFIG.DEBUG_SCREENSHOT_LOCATION["top"],
            CONFIG.DEBUG_SCREENSHOT_LOCATION["left"],
            refresh_rate_ms=self.sleep_seconds * 900,
            name=name,
        )

    def set_inventory_slice(self):
        """Sets self.inventory_slices by finding corner points on screen."""
        tl, tr, bl, br = get_inventory_corner_points(self.client)
        if all([tl, tr, bl, br]):
            # full_image[yi:yf,xi:xf]
            self.inventory_slices = (slice(tl[1], bl[1]), slice(tl[0], tr[0]))
            slots = calculate_inventory_slots(tl, tr, bl, br)
            self.inventory_slots = list(map(lambda slot: (slot[0]/2, slot[1]/2), slots))
        else:
            print("WARNING: Could not find inventory!")

    def is_amulet_equipped(self, debug=False):
        screenshot = get_screenshot_bgr(CONFIG.AMULET_WINDOW)
        self.debug_display(screenshot)
        amulet = cv2.imread("pics/amulet_of_chem.png", cv2.IMREAD_COLOR)
        tl, _ = get_image_on_screen(screenshot, amulet, image_name="amulet", debug=debug)
        return bool(tl)
