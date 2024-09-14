
import time
import cv2
from dataclasses import dataclass

from script_random import rsleep
from script_utils import (
    display_debug_screenshot,
    get_screenshot_bgr,
    get_image_on_screen,
)

from auto_gui import slow_click_in_rect, press_key
from .base import ScriptBase
import http_plugin.item_ids as item_ids
from http_plugin.inventory import Inventory

class CONFIG:
    # Size of entire monitor
    MONITOR_SIZE = {"width": 1727, "height": 1116}
    # Size of game window
    # Includes title bar because it makes clicking more straight forward.
    GAME_WINDOW = {"top": 0, "left": 0, "width": 1120, "height": 1059}
    DEBUG_SCREENSHOT_SIZE = (500, 500)
    DEBUG_SCREENSHOT_LOCATION = {"top": 0, "left": MONITOR_SIZE["width"] - DEBUG_SCREENSHOT_SIZE[0]}

MITH_BAR = cv2.imread("pics/mith_bar_bank.png", cv2.IMREAD_COLOR)
ANVIL = cv2.imread("pics/anvil_prif.png", cv2.IMREAD_COLOR)
ANVIL_VERTICAL = cv2.imread("pics/anvil_prif_vertical.png", cv2.IMREAD_COLOR)
PLATEBODY_INV = cv2.imread("pics/mith_platebody_inv.png", cv2.IMREAD_COLOR)
PLATEBODY_MENU = cv2.imread("pics/mith_platebody_menu.png", cv2.IMREAD_COLOR)
PRIF_BANK = cv2.imread("pics/prif_bank.png", cv2.IMREAD_COLOR)
PRIF_BANK_VERTICAL = cv2.imread("pics/prif_bank_vertical.png", cv2.IMREAD_COLOR)
DEPOSIT_ALL = cv2.imread("pics/deposit_all.png", cv2.IMREAD_COLOR)

WALK_TO_BANK_TIME = 3

# Amount of time to sleep each loop.
LAG_FACTOR = 0.25

"""
python3.10 new_main.py --script PrifSmithing -n 1

Entity hider on
Fill bottom-two slots of inventory
hammer in first slot
look south
Reset zoom to 300
bank pin entered, Quantity All
No weapon equipped
"""
@dataclass
class PrifSmithing(ScriptBase):
    sleep_seconds: int = 0.1

    def on_start(self):
        print("Starting...")
        self.inv = Inventory()
        self.click_cache_coor = {}
        self.menu_region = CONFIG.GAME_WINDOW

        self.previous_inventory = None
        self.inventory_stale_count = 0

    def on_stop(self):
        print("Stopping...")

    def on_loop(self):
        time.sleep(LAG_FACTOR)
        # self.debug = copy(self.client)
        # self.debug_display(self.debug)
        bank_open = self.is_bank_open()
        inv_full = self.inv.is_full()
        has_bars = self.inv.has_item(item_ids.MITHRIL_BAR)
        has_platebodies = self.inv.has_item(item_ids.MITHRIL_PLATEBODY)

        self.check_inventory_changed()
        if self.inventory_stale_count >= 10:
            print("Inventory stale, exiting")
            press_key("esc")
            # self.try_to_click_cached("pics/logout.png", "LOGOUT")
            exit()
    
        # Bank menu open
        # 
        if bank_open:
            if has_platebodies:
                print("depositing platebodies")
                clicked = self.try_to_click_cached(PLATEBODY_INV, "PLATEBODY_INV")
                if clicked:
                    time.sleep(LAG_FACTOR)
            elif not has_platebodies and not has_bars:
                print("withdrawing bars")
                clicked = self.try_to_click_cached(MITH_BAR, "MITH_BAR")
                if clicked:
                    time.sleep(LAG_FACTOR)
            elif not has_platebodies and has_bars:
                print("clicking anvil")
                self.try_to_click_cached(ANVIL, "ANVIL")
                self.wait_for(self.is_smithing_menu_open)
        # Smithing menu open
        # 
        elif self.is_smithing_menu_open():
            print("smithing platebodies")
            self.try_to_click_cached(PLATEBODY_MENU, "PLATEBODY_MENU")
            rsleep(5)

        # 
        # No menu open
        # 

        # Missed the anvil?
        elif inv_full and has_bars:
            print("clicking anvil vertical")
            self.try_to_click_cached(ANVIL_VERTICAL, "ANVIL_VERTICAL")
            self.wait_for(self.is_smithing_menu_open, max_wait=3)
        # Still smithing
        elif not inv_full and has_bars:
            print("waiting for smithing...")
            rsleep(5)
        # Done smithing
        elif not inv_full and not has_bars:
            print("opening bank")
            clicked = self.try_to_click_cached(PRIF_BANK, "PRIF_BANK")
            if clicked:
                print("walking to bank")
                self.wait_for(self.is_bank_open)
            else:
                print("opening bank vertical")
                clicked = self.try_to_click_cached(PRIF_BANK_VERTICAL, "PRIF_BANK_VERTICAL")
        else:
            print(
                "Missed all cases:",
                self.inv,
                bank_open,
                inv_full,
                has_bars,
                has_platebodies,
                sep="\n",
            )


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

    # def try_to_click(self, img, cache_name):
    #     screenshot = get_screenshot_bgr(CONFIG.GAME_WINDOW)
    #     tl, br = get_image_on_screen(screenshot, img)
    #     if tl:
    #         slow_click_in_rect(tl, br)
    #         return True
    #     else:
    #         print(f"couldn't find {cache_name}")
    #         return False
        
    def try_to_click_cached(self, img, cache_name):
        cached_coor = self.click_cache_coor.get(cache_name)
        if cached_coor:
            cached_region = self.region_from_cooridinates(cached_coor)
            screenshot = get_screenshot_bgr(cached_region)
        else:
            screenshot = get_screenshot_bgr(CONFIG.GAME_WINDOW)
        
        tl, br = get_image_on_screen(screenshot, img)

        # If found in cache, we need to use region to click
        if tl and cached_coor:
            slow_click_in_rect(cached_coor[0], cached_coor[1])
            return True
        # If found outside cache, use image rect.
        elif tl:
            self.click_cache_coor[cache_name] = (tl, br)
            slow_click_in_rect(tl, br)
            return True
        else:
            print(f"couldn't find {cache_name}")
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
        
    # Check if the bank is open by looking for the DEPOSIT_ALL icon.
    # Once found, cache the area to look for to make checking faster.
    def is_bank_open(self):
        cached_coor = self.click_cache_coor.get("DEPOSIT_ALL")
        if cached_coor:
            cached_region = self.region_from_cooridinates(cached_coor)
            screenshot = get_screenshot_bgr(cached_region)
        else:
            screenshot = get_screenshot_bgr(CONFIG.GAME_WINDOW)

        tl, br = get_image_on_screen(screenshot, DEPOSIT_ALL)
        if tl and not cached_coor:
            self.click_cache_coor["DEPOSIT_ALL"] = (tl, br)

        return tl

    # Check if the menu is open by looking for the plate body icon.
    # Once found, cache the area to look for to make checking faster.
    def is_smithing_menu_open(self):
        cached_coor = self.click_cache_coor.get("PLATEBODY_MENU")
        if cached_coor:
            cached_region = self.region_from_cooridinates(cached_coor)
            screenshot = get_screenshot_bgr(cached_region)
        else:
            screenshot = get_screenshot_bgr(CONFIG.GAME_WINDOW)

        tl, br = get_image_on_screen(screenshot, PLATEBODY_MENU)
        if tl and not cached_coor:
            self.click_cache_coor["PLATEBODY_MENU"] = (tl, br)

        return tl
    
    # Waits until the function returns true, up to max number of seconds
    # func: Takes a unary function
    # max_wait: Maximum number of seconds to wait
    def wait_for(self, func, args=(), max_wait=10):
        start = time.time()
        elapsed = 0

        while elapsed <= max_wait:
            print(f"{func.__name__}? {elapsed}")
            if func(*args):
                return True
            elapsed = time.time() - start
            time.sleep(0.2)
        return False
    
    def check_inventory_changed(self):
        if self.inv.i == self.previous_inventory:
            self.inventory_stale_count += 1
        else:
            self.inventory_stale_count = 0
        self.previous_inventory = self.inv.i