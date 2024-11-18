import os
import cv2
from dataclasses import dataclass
import pytesseract
import numpy
import pyautogui

from script_random import rsleep
from script_utils import (
    display_debug_screenshot,
    get_screenshot_bgr,
    get_screenshot,
    get_image_on_screen,
    get_rectangle,
)
from colors import get_mask

from auto_gui import slow_click_in_rect, click_in_rect
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
    # NOT STRETCHED!
    CHAT_WINDOW = {"top": 851, "left": 8, "width": 637, "height": 148}
    DEBUG_SCREENSHOT_SIZE = (500, 500)
    DEBUG_SCREENSHOT_LOCATION = {"top": 0, "left": MONITOR_SIZE["width"] - DEBUG_SCREENSHOT_SIZE[0]}

SPECIAL = cv2.imread("pics/wt_special_attack_full.png", cv2.IMREAD_COLOR)
BRAZIER_TILE = cv2.imread("pics/wt_brazier_tile.png", cv2.IMREAD_COLOR)
ROOTS_TILE = cv2.imread("pics/wt_roots_tile.png", cv2.IMREAD_COLOR)
ROOTS = cv2.imread("pics/wt_roots.png", cv2.IMREAD_COLOR)
BRAZIER_COLOR = numpy.array([255, 0, 255])

# Amount of time to sleep each loop.
LAG_FACTOR = 0

"""
python3.10 new_main.py --script PrifSmithing -n 1

look West
Reset zoom to 300
Entity Hider
Line of Sight off
Stretch mode 30%

hammer in first slot, knife in second
"""
@dataclass
class Wintertodt(ScriptBase):
    sleep_seconds: int = 0.1

    def on_start(self):
        self.last_log = ""

        self.log("Starting Script...")
        self.inv = Inventory()
        self.stats = Stats()
        self.click_cache_coor = {}
        self.last_message, self.previous_message = "", ""
        self.previous_iteration_message = ""
        self.previous_iteration_time = ""

        self.previous_inventory = None
        self.inventory_stale_count = 0

    def on_stop(self):
        self.log("Stopping Script...")

    def on_loop(self):
        # self.debug = copy(self.client)
        # self.debug_display(self.debug)
        self.check_inventory_changed()
        self.get_last_messages()

        if self.round_ended():
            self.log("Round ended. Waiting.")
            pass
        elif self.round_start():
            self.log("Round started")
            self.try_to_click(ROOTS_TILE, 0.9)
            self.try_to_click(SPECIAL, 0.9)
            rsleep(5, 0.1)
            self.try_to_click(ROOTS, 0.9)

        elif self.inv.is_full():
            self.log("inventory full")
            enough_kindling = self.inv.i[5]['id'] == item_ids.BRUMA_KINDLING
            # If we haven't finished fletching some
            # 
            # We haven't fletched any
            if self.inv.i[2]['id'] != item_ids.BRUMA_KINDLING:
                self.fletch()
            elif not self.inventory_stale() and not enough_kindling:
                pass
            # Interrupted from fletching
            # [5] is arbitrarily where fletch() decides to click.
            elif not enough_kindling:
                self.log("stale and need to fletch more")
                self.fletch()
            else:
                self.try_to_click(BRAZIER_TILE, 0.9)
                rsleep(3, 0.1)
                self.click_brazier()

        elif self.recently_interrupted() and not self.inv.is_full():
            self.log("interrupted")
            if self.inventory_empty():
                self.out_of_roots()
            else:
                self.click_brazier()

        elif self.inventory_stale():
            self.log("inventory stale")
            if self.inventory_empty():
                self.out_of_roots()
            else:
                self.click_brazier()
        else:
            self.log("still chopping/burning")


    def on_sleep(self):
        rsleep(LAG_FACTOR)

    def click_brazier(self):
        self.log("clicking brazier")
        try:
            screenshot = get_screenshot(CONFIG.GAME_WINDOW)
            tl, br = self.get_color_rect(screenshot, BRAZIER_COLOR)
        # Failed to find color.
        # Move mouse out of the way and try again.
        except TypeError:
            pyautogui.moveTo(100, 100)
            screenshot = get_screenshot(CONFIG.GAME_WINDOW)
            tl, br = self.get_color_rect(screenshot, BRAZIER_COLOR)

        slow_click_in_rect(tl, br)
        pyautogui.moveRel(0, 50)
        rsleep(2.5, 0.1)

    def round_start(self):
        has_roots = self.inv.has_item(item_ids.BRUMA_ROOT)
        msg = "about to start"
        has_message = msg in self.last_message or msg in self.previous_message
        return (not has_roots and has_message and self.chatbox_changed)

    def round_ended(self):
        msg1 = "did not earn enough"
        msg2 = "rewards"
        start_msg = "about to start"
        return (
            msg1 in self.previous_message or msg2 in self.previous_message
            ) and not (
            start_msg in self.last_message
            )

    def out_of_roots(self):
        self.log("Out of roots")
        self.try_to_click(ROOTS_TILE, 0.9)
        rsleep(4, 0.1)
        self.try_to_click(ROOTS, 0.95)

    # Not actually empty, but only hammer and knife
    def inventory_empty(self):
        has_roots = self.inv.has_item(item_ids.BRUMA_ROOT)
        has_kindling = self.inv.has_item(item_ids.BRUMA_KINDLING)
        return not has_roots and not has_kindling

    def recently_interrupted(self):
        msg = "interrupted"
        return msg in self.last_message and self.chatbox_changed

    def fletch(self):
        self.log("fletching")
        slow_click_in_rect((960*2, 640*2), (965*2, 655*2))
        slow_click_in_rect((950*2, 687*2), (970*2, 702*2))
        rsleep(3, 0.1)

    def get_color_rect(self, image, color):
        mask = get_mask(image, color)
        rect = get_rectangle(mask, color_name=color)
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
        os.system('afplay /System/Library/Sounds/Sosumi.aiff')
        os.system('afplay /System/Library/Sounds/Sosumi.aiff')
        os.system('afplay /System/Library/Sounds/Sosumi.aiff')

    # Sets the self.last_message and self.previous_message instance vars.
    # These represent the last two messages in the chat box.
    # 
    # This method also sets self.chatbox_changed, which is the main
    # way to know that your messages aren't stale.
    # Usage:
    # msg = "foo"
    # return msg in self.last_message and self.chatbox_changed
    def get_last_messages(self):
        text = self.get_chatbox_text()
        last_time = []
        try:
            last_time, self.last_message = text[-1]
            previous_time, self.previous_message = text[-2]
        except IndexError:
            pass

        if self.previous_iteration_time == last_time and self.previous_iteration_message == self.last_message:
            self.chatbox_changed = False
        else:
            self.chatbox_changed = True
            self.previous_iteration_time = last_time
            self.previous_iteration_message = self.last_message

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
        self.inv.reload()
        if self.inv.i == self.previous_inventory:
            self.inventory_stale_count += 1
        else:
            self.inventory_stale_count = 0
        self.previous_inventory = self.inv.i

    # If this is too low compared to LAG_FACTOR, it will
    #  get triggered incorrectly. Setting it to 2 for 2 seems okay.
    # Setting it to X for 0 LAG_FACTOR seems to wrok.
    def inventory_stale(self, max=5):
        return self.inventory_stale_count > max
    
    def log(self, msg):
        if self.last_log != msg:
            print(msg)
            self.last_log = msg

