from auto_gui import click, press_key, click_in_rect
from script_utils import wait_for_bank
from script_random import random_point_near_center_of_rect, rsleep


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
