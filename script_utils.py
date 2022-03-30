from math import hypot, inf
from os import closerange
import time

import cv2
import numpy
import mss

from colors import BANK_TEXT_COLOR, SOLID_GREEN, get_mask
from auto_gui import click
from settings import MONITOR, FISHING_STATUS, INVENTORY_SLOT_RECTS_ABSOLUTE, CENTER_OF_SCREEN_RELATIVE, DEBUG
from script_random import rsleep, random_point_near_center_of_rect


def get_screenshot(monitor=MONITOR):
    with mss.mss() as screenshot:
        return numpy.array(screenshot.grab(monitor))


def get_screenshot_bgr():
    screenshot = get_screenshot()
    return cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)


def is_image_on_screen(image, threshold=0.80):
    # Get the current screen
    screenshot = get_screenshot_bgr()
    # Find match
    result = cv2.matchTemplate(screenshot, image, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    # Check if match
    return max_val > threshold


def get_rectangle(mask, color_name):
    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 1:
        print(f"Warning! More than one rect for {color_name}")
        return
    try:
        x, y, w, h = cv2.boundingRect(contours[0])
    except IndexError as e:
        print(f"Couldn't find {color_name}")
        exit()
    top_left = (x, y)
    bottom_right = (x + w, y + h)
    return (top_left, bottom_right)


def get_closest_rectangle_to_center(color):
    """Gets the closest `color` rectangle to the center of the screen (settings.CENTER_OF_SCREEN_RELATIVE).
    This is because the player is almost always in the center."""
    frame = get_screenshot()
    mask = get_mask(frame, color)
    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    rectangles = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        top_left = (x, y)
        bottom_right = (x + w, y + h)
        rectangles.append((top_left, bottom_right))

    closest_rect = None
    closest_distance = inf
    for rect in rectangles:
        center_x, center_y = random_point_near_center_of_rect(*rect)
        distance = hypot(
            center_x - CENTER_OF_SCREEN_RELATIVE[0],
            center_y - CENTER_OF_SCREEN_RELATIVE[1],
        )
        if DEBUG:
            print(f"{center_x},{center_y}: {distance}")
        if distance < closest_distance:
            closest_rect = rect
            closest_distance = distance

    return closest_rect


def wait_for_bank(click_coor=None):
    """click_while_waiting expects an (x,y) to click within"""
    inside_bank = False
    while not inside_bank:
        if click_coor:
            click(click_coor[0], click_coor[1])
            rsleep(0.25)
        frame = get_screenshot()
        bank_amount_mask = get_mask(frame, BANK_TEXT_COLOR)
        inside_bank = numpy.any(bank_amount_mask)
        if not click_coor:
            time.sleep(0.1)  # Benkmarked at .033 without


def wait_for_deposit_all(click_coor):
    empty_inventory_pic = cv2.imread("pics/empty_inventory.png", cv2.IMREAD_COLOR)
    start = time.time()
    empty_inventory = False
    click(*click_coor)
    while not empty_inventory:
        if time.time() - start >= 1.5:
            click(*click_coor)
        empty_inventory = is_image_on_screen(empty_inventory_pic)
        # time.sleep(0.1)  # Benkmarked at ~0.18 without


def reset_xp_tracker():
    click(825, 325)
    click(825, 325, button="right")
    click(840, 362)


def drop_all(slots_to_click, time_to_move=(0.12, 0.03)):
    """left click only at the moment"""
    for slot_index in slots_to_click:
        x, y = random_point_near_center_of_rect(*INVENTORY_SLOT_RECTS_ABSOLUTE[slot_index - 1], absolute=True)
        # time_to_move=(0.05, 0.01) is WAY too fast
        # The default of time_to_move=(0.15, 0.05) feels good for nearly all activities except dropping
        # your inventory quickly. A human doing it hundreds of times is a fair bit faster.
        click(x, y, time_to_move=time_to_move)
