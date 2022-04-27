import math
import cv2
import numpy
from auto_gui import slow_click
from colors import SOLID_GREEN, get_mask
from script_random import random_point_near_center_of_rect, rsleep
from script_utils import drop_all, get_closest_rectangle_to_center, get_screenshot, is_image_on_screen
from settings import FISHING_STATUS, SPECIAL_ATTACK_RECHARGE_SECONDS, WOODCUTTING_DROP_ORDER


BLISTERWOOD_INV_FULL = cv2.imread("pics/inv_full_of_blisterwood_logs.png", cv2.IMREAD_COLOR)


class Woodcutting:
    def __init__(self, tree_rect_color, special_attack_color, seconds_elapsed):
        self.tree_rect_color = tree_rect_color
        self.special_attack_color = special_attack_color
        self.seconds_elapsed = seconds_elapsed
        self.already_specialed = set()
        self.state = None

    def update_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            print(self.state)

    def is_chopping(self):
        frame = get_screenshot(monitor=FISHING_STATUS)
        status_mask = get_mask(frame, SOLID_GREEN)
        is_actively_chopping = numpy.any(status_mask)
        return is_actively_chopping

    #  TODO - gotta not reset the state between runs for this to work.
    # def maybe_click_special_attack(self):
    #     """
    #     Click on self.special_attack_color
    #     """
    #     # 0-299 seconds = 0, 300-599 seconds = 1, etc.
    #     special_attack_count = math.trunc(self.seconds_elapsed / SPECIAL_ATTACK_RECHARGE_SECONDS)
    #     if special_attack_count not in self.already_specialed:
    #         print(
    #             f"Clicking special attack. Count: {special_attack_count} Sec: {self.seconds_elapsed}, Past: {self.already_specialed}"
    #         )
    #         self.already_specialed.add(special_attack_count)
    #         rect = get_closest_rectangle_to_center(color=self.special_attack_color)
    #         x, y = random_point_near_center_of_rect(*rect)
    #         slow_click(x, y)
    #         rsleep(0.25)
    #     else:
    #         print(
    #             f"NOT Clicking special attack. Count: {special_attack_count} Sec: {self.seconds_elapsed}, Past: {self.already_specialed}"
    #         )

    def blisterwood(self):

        if self.is_chopping():
            self.update_state("Woodcutting")
        else:
            self.update_state("Idle")

            if is_image_on_screen(BLISTERWOOD_INV_FULL, threshold=0.85):
                self.update_state("Inventory full")
                drop_all(WOODCUTTING_DROP_ORDER)

            # self.maybe_click_special_attack()

            rect = get_closest_rectangle_to_center(color=self.tree_rect_color)
            x, y = random_point_near_center_of_rect(*rect)
            slow_click(x, y)

        rsleep(5)
