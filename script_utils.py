from math import hypot, inf
import math
from os import closerange
from ssl import ALERT_DESCRIPTION_ILLEGAL_PARAMETER
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


def get_screenshot_bgr(monitor=MONITOR):
    screenshot = get_screenshot(monitor)
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


def get_closest_rectangle_to_center(color, image=None):
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
        debug_rectangle(image, rect[0], rect[1])
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


def debug_rectangle(image, top_left, bottom_right):
    cv2.rectangle(
        image,
        top_left,
        bottom_right,
        [0, 0, 255],
        2,
    )


def debug_point(image, x, y, width=5):
    cv2.circle(
        image,
        (x, y),
        radius=width,
        color=(255, 255, 0),
        thickness=-1,
    )


def debug_line(image, start_point, end_point, width=5):
    cv2.line(
        image,
        start_point,
        end_point,
        color=(255, 255, 0),
        thickness=width,
    )


THRESHOLD = 0.85


def debug_images_on_screen(screenshot, images: list):
    """
    Draws red boxes around the list of images on the screen.
    Draws them onto screenshot. Expects something else to imshow screenshot.
    """
    for image in images:
        top_left, bottom_right = get_image_on_screen(screenshot, image, threshold=THRESHOLD)
        debug_rectangle(screenshot, top_left, bottom_right)


def debug_points_on_screen(screenshot, points: list, width=5):
    """
    Draws cyan circles where each of the points are.
    Draws them onto screenshot. Expects something else to imshow screenshot.
    """
    for point in points:
        debug_point(screenshot, point[0], point[1], width)


def get_image_on_screen(screenshot, image, threshold=0.85):
    result = cv2.matchTemplate(screenshot, image, cv2.TM_CCOEFF_NORMED)
    w, h = image.shape[:2]
    matching_points = numpy.where(result >= threshold)
    all_matches = zip(*matching_points[::-1])
    # Throwing away all but one match. There could be multiple here.
    try:
        top_left = list(all_matches)[0]
    except IndexError:
        print("Couldn't find inventory")
        return None, None
    bottom_right = (top_left[0] + w, top_left[1] + h)
    return top_left, bottom_right


def display_debug_screenshot(screenshot, monitor=MONITOR, refresh_rate_ms=1000):
    """
    params:
        monitor: Where on the screen to screenshot
        refresh_rate_ms: milliseconds to wait between refresh
    """
    # This will resize the screenshot to the size of the thing you actually screenshot.
    # That way when you display (imshow) it, it's the same size as the thing you screenshot.
    # Otherwise it's fullscreen.
    resized = cv2.resize(screenshot, (monitor["width"], monitor["height"]))
    cv2.imshow("Game Preview", resized)
    cv2.waitKey(delay=refresh_rate_ms)


def get_inventory_corner_points(screenshot):
    # Top Left of Inventory
    top_left_im = cv2.imread("pics/inventory_top_left.png", cv2.IMREAD_COLOR)
    top_left_invent_point, _ = get_image_on_screen(screenshot, top_left_im)
    # Top Right of Inventory
    top_right_im = cv2.imread("pics/inventory_top_right.png", cv2.IMREAD_COLOR)
    w, _ = top_right_im.shape[:2]
    top_left, _ = get_image_on_screen(screenshot, top_right_im)
    top_right_invent_point = (top_left[0] + w, top_left[1])
    # Bottom Left of Inventory
    bottom_left_im = cv2.imread("pics/inventory_bottom_left.png", cv2.IMREAD_COLOR)
    _, h = bottom_left_im.shape[:2]
    top_left, _ = get_image_on_screen(screenshot, bottom_left_im)
    bottom_left_invent_point = (top_left[0], top_left[1] + h)
    # Bottom Right of Inventory
    bottom_right_im = cv2.imread("pics/inventory_bottom_right.png", cv2.IMREAD_COLOR)
    _, bottom_right_invent_point = get_image_on_screen(screenshot, bottom_right_im)

    return top_left_invent_point, top_right_invent_point, bottom_left_invent_point, bottom_right_invent_point

def get_inventory_slots(monitor):
    screenshot = get_screenshot_bgr(monitor)
    tl, tr, bl, br = get_inventory_corner_points(screenshot)
    return calculate_inventory_slots(tl, tr, bl, br)

def calculate_inventory_slots(top_left, top_right, bottom_left, bottom_right):
    """
    This is ugly and I'm ashamed and it works. ':D
    """
    # column_height = bottom_left[1] - top_left[1]

    LEFT_RIGHT_ADJUST_FRACTION = 0.03
    COLUMN_WIDTH_DIVIDE = 5

    width = top_right[0] - top_left[0]
    LEFT_RIGHT_ADJUST = math.floor(width * LEFT_RIGHT_ADJUST_FRACTION)
    left = top_left[0] - LEFT_RIGHT_ADJUST
    top = top_left[1]
    right = bottom_right[0] + LEFT_RIGHT_ADJUST
    bottom = bottom_right[1]
    column_width = (right - left) // COLUMN_WIDTH_DIVIDE

    x_values = []
    for col in range(1, 5):
        x_values.append(math.floor(left + column_width * col))

    TOP_BOTTOM_ADJUST_FRACTION = 0.02
    ROW_WIDTH_DIVIDE = 8

    height = bottom_left[1] - top_left[1]
    TOP_BOTTOM_ADJUST = math.floor(height * TOP_BOTTOM_ADJUST_FRACTION)
    left = top_left[0]
    top = top_left[1] - TOP_BOTTOM_ADJUST
    right = bottom_right[0]
    bottom = bottom_right[1] + TOP_BOTTOM_ADJUST * 2
    row_width = (bottom - top) // ROW_WIDTH_DIVIDE

    inventory_points = []

    for row in range(1, 8):
        y = math.floor(top + row_width * row)
        for x in x_values:
            inventory_points.append((x, y))

    return inventory_points
