import os
import cv2
from dataclasses import dataclass
import pytesseract

from script_random import rsleep, random_around
from script_utils import (
    display_debug_screenshot,
    get_screenshot_bgr,
    get_image_on_screen,
)

from auto_gui import slow_click_in_rect
from .base import ScriptBase
import http_plugin.item_ids as item_ids
from http_plugin.inventory import Inventory
from http_plugin.stats import Stats

class CONFIG:
    # Size of entire monitor
    MONITOR_SIZE = {"width": 1727, "height": 1116}
    # Size of game window
    # Includes title bar because it makes clicking more straight forward.
    GAME_WINDOW = {"top": 0, "left": 0, "width": 1120, "height": 1059}
    CHAT_WINDOW = {"top": 836, "left": 8, "width": 690, "height": 159}
    DEBUG_SCREENSHOT_SIZE = (500, 500)
    DEBUG_SCREENSHOT_LOCATION = {"top": 0, "left": MONITOR_SIZE["width"] - DEBUG_SCREENSHOT_SIZE[0]}

CANNON = cv2.imread("pics/cannon-center-300.png", cv2.IMREAD_COLOR)
SHARK = cv2.imread("pics/shark.png", cv2.IMREAD_COLOR)
PRAYER_POTION = cv2.imread("pics/prayer_potion.png", cv2.IMREAD_COLOR)

# Amount of time to sleep each loop.
LAG_FACTOR = 15
EAT_THRESHOLD = 60
PRAYER_THRESHOLD = 40

"""
python3.10 new_main.py --script PrifSmithing -n 1

look north
Reset zoom to 300
Entity Hider
 - Hide Attacker
 - Hide NPC 2D
 - Hide Local Player
 - Hide Local Player 2D
Stretched mode off
"""
@dataclass
class Slayer(ScriptBase):
    sleep_seconds: int = 0.1

    def on_start(self):
        print("Starting...")
        self.inv = Inventory()
        self.stats = Stats()
        self.click_cache_coor = {}
        self.menu_region = CONFIG.GAME_WINDOW

        self.previous_inventory = None
        self.inventory_stale_count = 0

    def on_stop(self):
        print("Stopping...")

    def on_loop(self):
        # self.debug = copy(self.client)
        # self.debug_display(self.debug)
        
        is_cannon_low = True

    
        # Bank menu open
        # 
        if is_cannon_low:
            self.click_cannon()
            rsleep(1)

        if self.is_health_low():
            self.eat()
            rsleep(1)

        if self.is_prayer_low():
            self.sip_potion()
            rsleep(1)

        rsleep(LAG_FACTOR)


    def on_sleep(self):
        pass

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

    def region_from_cooridinates(self,  cooridinates):
        tl, br = cooridinates
        left, top = tl
        right, bottom = br
        width = (bottom - top) + 40
        height = (right - left) + 40
        region = {"top": (top - 20) / 2,
                            "left": (left - 20) / 2,
                            "width": width / 2,
                            "height": height / 2}
        # print(f"cached region: {region}")
        return region
        
    def click_cannon(self):
        self.try_to_click(CANNON, 0.6)

    def is_health_low(self):
        current, max = self.stats.hp()
        is_low = current <= random_around(EAT_THRESHOLD, 0.25)
        if is_low:
            print(f"HP low {current}. Eating.")
            return True
        else:
            return False

    def eat(self):
        if self.inv.has_item(item_ids.SHARK):
            self.try_to_click(SHARK, 0.8)
        else:
            print("OUT OF FOOD!")
            self.alert()
    
    def is_prayer_low(self):
        current, max = self.stats.prayer()
        is_low = current <= random_around(PRAYER_THRESHOLD, 0.25)
        if is_low:
            print(f"Prayer low {current}/{max}. Sipping potion.")
            return True
        else:
            return False
    
    def sip_potion(self):
        if self.inv.has_any_items([
            item_ids.PRAYER_POTION1, item_ids.PRAYER_POTION2,
            item_ids.PRAYER_POTION3, item_ids.PRAYER_POTION4,
            ]):
            self.try_to_click(PRAYER_POTION, 0.8)
        else:
            print("OUT OF PRAYER POTS!")
            self.alert()

    def alert(self):
        os.system('afplay /System/Library/Sounds/Sosumi.aiff')
        os.system('afplay /System/Library/Sounds/Sosumi.aiff')
        os.system('afplay /System/Library/Sounds/Sosumi.aiff')

    def get_chatbox_text(self, monitor=CONFIG.CHAT_WINDOW):
        color_screenshot = get_screenshot_bgr(monitor)
        text_lines = pytesseract.image_to_string(color_screenshot).split("\n")
        text_lines = [line for line in text_lines if line != '']
        # print(text_lines)
        output = []
        for line in text_lines:
            split_line = line.split("] ")
            output_line = []
            if len(split_line) == 1:
                output_line.append("")
                output_line.append(split_line[0])
            else:
                output_line.append(split_line[0])
                output_line.append(split_line[1])
            output.append(output_line)
        return output
    
    def check_inventory_changed(self):
        if self.inv.i == self.previous_inventory:
            self.inventory_stale_count += 1
        else:
            self.inventory_stale_count = 0
        self.previous_inventory = self.inv.i
        print(self.inventory_stale_count)

    def inventory_stale(self, max=10):
        return self.inventory_stale_count > max