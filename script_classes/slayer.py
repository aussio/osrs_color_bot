from dataclasses import dataclass
from copy import copy

import numpy
from script_classes.timer import timer
from script_classes.tesseract import img_to_str_bw_processing
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
    GAME_WINDOW = {"top": 0, "left": 0, "width": 769, "height": MONITOR_SIZE["height"]}
    DEBUG_SCREENSHOT_LOCATION = {"top": 0, "left": MONITOR_SIZE["width"] - GAME_WINDOW["width"]}


class CONSTANTS:
    WINDOW_TITLE_BAR_HEIGHT = 25

    class PRIMARY_STATS:
        """The dimensions for HP, Prayer, and Run
        All the numbers are * 2 because the screenshot dimensions are double the Mac dimensions for some reason.
        """

        BOX_HEIGHT = 13 * 2
        BOX_WIDTH = 20 * 2
        HP_TOP = 89 * 2
        HP_LEFT = 207 * 2
        PRAYER_TOP = 123 * 2
        PRAYER_LEFT = 207 * 2
        RUN_TOP = 155 * 2
        RUN_LEFT = 196 * 2


@dataclass
class Slayer(ScriptBase):

    # Client screenshot (Mat = Matrix)
    client: numpy.ndarray = None
    # Debug screenshot
    debug: numpy.ndarray = None
    # Stats
    hp: int = 0
    prayer: int = 0
    run_energy: int = 0
    # Slices used for partial screenshot matching
    # Also where prayer, spellbook, etc show.
    inventory_slices: tuple[slice] = None
    hp_slices: tuple[slice] = None
    prayer_slices: tuple[slice] = None
    run_slices: tuple[slice] = None

    sleep_seconds: int = 0.1

    def on_start(self):
        print("Starting...")
        self.client = get_screenshot_bgr(CONFIG.GAME_WINDOW)
        self.debug = copy(self.client)
        self.set_inventory_slice()
        self.set_primary_stats_slices()

    def on_stop(self):
        print("Stopping...")

    def on_loop(self):
        """
        print(f"Loop count: {self.loop_count}")
        if self.inventory_slices:
            inv = self.debug[self.inventory_slices[0], self.inventory_slices[1]]
            self.debug_display(inv, name="inventory")
        """
        self.client = get_screenshot_bgr(CONFIG.GAME_WINDOW)
        self.debug = copy(self.client)
        self.set_primary_stats()
        print(f"HP: {self.hp} Prayer: {self.prayer} Run: {self.run_energy}")

    def on_sleep(self):
        rsleep(self.sleep_seconds)

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
        else:
            print("WARNING: Could not find inventory!")

    def set_primary_stats_slices(self):
        """Sets self.hp_slice, self.prayer_slice, and self.run_slice.

        Finds them relative to the logout button on screen.

        All the numbers are * 2 because the screenshot dimensions are double the Mac dimensions for some reason.
        """
        BOX_HEIGHT = CONSTANTS.PRIMARY_STATS.BOX_HEIGHT
        BOX_WIDTH = CONSTANTS.PRIMARY_STATS.BOX_WIDTH
        CLIENT_WIDTH = CONFIG.GAME_WINDOW["width"] * 2

        hp_left = CLIENT_WIDTH - CONSTANTS.PRIMARY_STATS.HP_LEFT
        hp_top = CONSTANTS.PRIMARY_STATS.HP_TOP
        self.hp_slices = (slice(hp_top, hp_top + BOX_HEIGHT), slice(hp_left, hp_left + BOX_WIDTH))

        prayer_left = CLIENT_WIDTH - CONSTANTS.PRIMARY_STATS.PRAYER_LEFT
        prayer_top = CONSTANTS.PRIMARY_STATS.PRAYER_TOP
        self.prayer_slices = (slice(prayer_top, prayer_top + BOX_HEIGHT), slice(prayer_left, prayer_left + BOX_WIDTH))

        run_left = CLIENT_WIDTH - CONSTANTS.PRIMARY_STATS.RUN_LEFT
        run_top = CONSTANTS.PRIMARY_STATS.RUN_TOP
        self.run_slices = (slice(run_top, run_top + BOX_HEIGHT), slice(run_left, run_left + BOX_WIDTH))

    def set_primary_stats(self):
        self.set_hp()
        self.set_prayer()
        self.set_run_energy()

    def set_hp(self):
        """Seems to fail on 94"""
        hp = self.debug[self.hp_slices[0], self.hp_slices[1]]
        self.hp = img_to_str_bw_processing(hp)

    def set_prayer(self):
        prayer = self.debug[self.prayer_slices[0], self.prayer_slices[1]]
        self.prayer = img_to_str_bw_processing(prayer)

    def set_run_energy(self):
        run_energy = self.debug[self.run_slices[0], self.run_slices[1]]
        self.run_energy = img_to_str_bw_processing(run_energy)
