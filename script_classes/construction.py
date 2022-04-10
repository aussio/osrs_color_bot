from enum import Enum, auto
import cv2
import numpy
import pyautogui
from colors import SOLID_GREEN, get_mask
from script_random import random_point_near_center_of_rect, rsleep
from script_utils import get_closest_rectangle_to_center, get_rectangle, get_screenshot, is_image_on_screen
from auto_gui import click, press_key, click_in_rect, slow_click

EMPTY_INVENTORY = "../pics/construction-empty-inv.png"
BUTLER_RETRIEVED_ITEMS = "../pics/construction-butler-repeat.png"
BUTLER_GET_PLANKS = "../pics/construction-butler-repeat.png"
REALLY_REMOVE_FURNITURE = "../pics/construction-really-remove.png"


class STATES(Enum):
    ...


class Construction:
    def __init__(self, clickbox_rect_color, butler_color):
        self.set_clickbox_rect(clickbox_rect_color)
        self.set_clickbox_point()
        self.butler_color = butler_color
        self.STATE = None

    def set_clickbox_rect(self, clickbox_rect_color):
        """Only need to find thsi rect once. It won't move."""
        frame = get_screenshot()
        green_mask = get_mask(frame, clickbox_rect_color)
        self.clickbox_rect = get_rectangle(green_mask, color_name="green")

    def set_clickbox_point(self):
        """Want to re-get a point each time we click off to the butler and back."""
        self.clickbox_point = random_point_near_center_of_rect(self.clickbox_rect[0], self.clickbox_rect[1])

    def update_state(self, new_state):
        if Construction.STATE != new_state:
            Construction.STATE = new_state
            print(Construction.STATE)

    def is_empty_inventory(self):
        pic = cv2.imread(EMPTY_INVENTORY, cv2.IMREAD_COLOR)
        return is_image_on_screen(pic)

    def is_butler_retrieved_items(self):
        pic = cv2.imread(BUTLER_RETRIEVED_ITEMS, cv2.IMREAD_COLOR)
        return is_image_on_screen(pic)

    def is_butler_send_for_planks(self):
        pic = cv2.imread(BUTLER_GET_PLANKS, cv2.IMREAD_COLOR)
        return is_image_on_screen(pic)

    def is_really_remove_larder(self):
        pic = cv2.imread(REALLY_REMOVE_FURNITURE, cv2.IMREAD_COLOR)
        return is_image_on_screen(pic)

    # Compound functions =======================================

    def remove_larder(self, debug=False):
        if debug:
            print("remove click")
        slow_click(self.clickbox_point[0], self.clickbox_point[1], "right")
        slow_click(self.clickbox_point[0], self.clickbox_point[1], "left")
        if debug:
            print("remove hold")
        press_key("1", hold=1.5)
        if debug:
            print("remove unhold")

    def build_larder(self, debug=False):
        if debug:
            print("build click")
        slow_click(self.clickbox_point[0], self.clickbox_point[1], "right")
        slow_click(self.clickbox_point[0], self.clickbox_point[1], "left")
        if debug:
            print("build hold")
        press_key("2", hold=1.5)
        if debug:
            print("build unhold")

    def build_and_remove(self):
        self.build_larder()
        rsleep(1)
        self.remove_larder()

    def click_butler(self):
        butler_rect = get_closest_rectangle_to_center(color=self.butler_color)
        x, y = random_point_near_center_of_rect(butler_rect[0], butler_rect[1])
        slow_click(x, y)

    def butler_get_planks(self):
        self.click_butler()
        press_key("1", hold=1.5)

    def oak_larders(self):
        # if self.is_empty_inventory():
        #     self.butler_get_planks()

        self.build_and_remove()
        self.build_and_remove()

        self.butler_get_planks()

        self.set_clickbox_point()

        self.build_and_remove()

        rsleep(3.5, factor=0.1)
