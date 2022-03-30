import numpy
import pyautogui
import cv2
from auto_gui import click, press_key, click_in_rect
from colors import SOLID_GREEN, get_mask
from script_utils import (
    get_screenshot,
    wait_for_bank,
    wait_for_deposit_all,
    is_image_on_screen,
    get_closest_rectangle_to_center,
    drop_all,
)
from settings import CLEAN_CLICK_ORDER, FISHING_DROP_ORDER, FISHING_STATUS
from script_random import random_point_near_center_of_rect, rsleep


FISHING_INV_FULL = cv2.imread("pics/you_cant_carry_more_fish.png", cv2.IMREAD_COLOR)


def auto_craft(bank_rect, withdraw1_rect, item1_rect, item2_rect, wait_time, withdraw2_rect=None, lag_factor=1):
    # Open the bank
    x, y = random_point_near_center_of_rect(*bank_rect)
    click(x, y)
    # Deposit All
    wait_for_bank()
    click(x, y)
    rsleep(0.25 * lag_factor)
    # Withdraw <saved>
    click_in_rect(*withdraw1_rect)
    rsleep(0.25 * lag_factor)
    if withdraw2_rect:
        # Withdraw <saved>
        click_in_rect(*withdraw2_rect)
        rsleep(0.25 * lag_factor)
    # Esc bank
    press_key("esc")
    rsleep(0.50 * lag_factor)
    # Click item1
    click_in_rect(*item1_rect)
    rsleep(0.3)
    # Click item2
    click_in_rect(*item2_rect)
    # Make All
    press_key("space", hold=1.25 * lag_factor)
    rsleep(wait_time)


def auto_cast_superglass(bank_rect, withdraw1_rect, withdraw2_rect, cast_spell_rect):
    # Open the bank
    x, y = random_point_near_center_of_rect(*bank_rect)
    wait_for_bank(click_coor=(x, y))
    rsleep(0.25, factor=0.05)
    # Deposit All
    wait_for_deposit_all(click_coor=(x, y))
    # Withdraw shift+<saved> for withdraw 18 sand
    pyautogui.keyDown("shift")
    click_in_rect(*withdraw1_rect)
    pyautogui.keyUp("shift")
    rsleep(0.25)
    # With draw three seaweed
    x, y = random_point_near_center_of_rect(*withdraw2_rect)
    click(x, y)
    click(x, y)
    click(x, y)
    rsleep(0.25)
    # Esc bank
    press_key("esc")
    # Click Superglass Make
    click_in_rect(*cast_spell_rect)
    rsleep(1.95, factor=0.05)


def smith_platebodies_varrock(bank_booth_color, deposit_all, withdraw, anvil, platebody, start=0, lag_factor=1):
    def bank():
        closest_spot_rect = get_closest_rectangle_to_center(color=bank_booth_color)
        x, y = random_point_near_center_of_rect(closest_spot_rect[0], closest_spot_rect[1])
        # This delay is needed for some reason for the click to register
        pyautogui.moveTo(x, y)
        click(x, y)
        # Deposit All
        wait_for_bank()
        x, y = random_point_near_center_of_rect(*deposit_all)
        click(x, y)
        rsleep(0.25 * lag_factor)
        # Withdraw <saved>
        click_in_rect(*withdraw)
        rsleep(0.25 * lag_factor)

    def click_anvil():
        x, y = random_point_near_center_of_rect(*anvil)
        # This delay is needed for some reason for the click to register
        pyautogui.moveTo(x, y)
        click(x, y)
        rsleep(2.5)
        wait_for_bank()
        print("waiting for interface")

    def make_platebody():
        click_in_rect(*platebody)
        # Make All
        rsleep(15, 0.05)

    funcs = [bank, click_anvil, make_platebody]
    if start == 0:
        funcs[0]()
        funcs[1]()
        funcs[2]()
    elif start == 1:
        funcs[1]()
        funcs[2]()
        funcs[0]()
    elif start == 2:
        funcs[2]()
        funcs[0]()
        funcs[1]()


def clean_herbs():
    drop_all(CLEAN_CLICK_ORDER, time_to_move=(0.10, 0.05))


class Fishing:
    FISHING_STATE = None

    def is_fishing():
        frame = get_screenshot(monitor=FISHING_STATUS)
        fishing_mask = get_mask(frame, SOLID_GREEN)
        is_actively_fishing = numpy.any(fishing_mask)
        return is_actively_fishing

    def update_state(new_state):
        if Fishing.FISHING_STATE != new_state:
            Fishing.FISHING_STATE = new_state
            print(Fishing.FISHING_STATE)

    @classmethod
    def barbarian_fishing(cls, fishing_rect_color):

        if cls.is_fishing():
            cls.update_state("Fishing")
        else:
            cls.update_state("Not fishing")

            if is_image_on_screen(FISHING_INV_FULL):
                cls.update_state("Inventory full")
                drop_all(FISHING_DROP_ORDER)
                rsleep(1)

            closest_spot_rect = get_closest_rectangle_to_center(color=fishing_rect_color)
            x, y = random_point_near_center_of_rect(closest_spot_rect[0], closest_spot_rect[1])
            # This delay is needed for some reason for the click to register
            # on fishing spots.
            pyautogui.moveTo(x, y)
            click(x, y)

        rsleep(10)


