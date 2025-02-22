from math import hypot, inf
import math
import time

import cv2
import numpy
import mss

from colors import BANK_TEXT_COLOR, get_mask
from auto_gui import click
from settings import MONITOR, INVENTORY_SLOT_RECTS_ABSOLUTE, CENTER_OF_SCREEN_RELATIVE, DEBUG
from script_random import rsleep, random_point_near_center_of_rect


def get_screenshot(monitor=MONITOR):
    with mss.mss() as screenshot:
        return numpy.array(screenshot.grab(monitor))


def get_screenshot_bgr(monitor=MONITOR):
    """Takes from 0.075 to 0.1 seconds"""
    screenshot = get_screenshot(monitor)
    return cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

# Get a list of lines of text from the chatbox.
# Splits each line into an array of [timestamp, text]
# Fills in empty timestamp or text if unable to read it properly
# 
# for timestamp, text in chatbox:
#     print(timestamp, text)
def get_chatbox_text(monitor=MONITOR):
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


def is_image_on_screen(image, threshold=0.80):
    # Get the current screen
    screenshot = get_screenshot_bgr()
    # Find match
    result = cv2.matchTemplate(screenshot, image, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    # Check if match
    return max_val > threshold


def get_rectangle(mask, color_name, only_one=True):
    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if only_one and len(contours) > 1:
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


def wait_for_deposit_all(click_coor, img_filename="empty_inventory.png"):
    empty_inventory_pic = cv2.imread(f"pics/{img_filename}", cv2.IMREAD_COLOR)
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


def get_image_on_screen(screenshot, image, threshold=0.85, image_name="", debug=False):
    """Can be sped up if screenshot is relatively small compared to image.
    Basically matchTemplate works by sliding 'image' all across 'screenshot' until there's a match.

    See: https://stackoverflow.com/questions/44218626/increase-performance-of-template-matching-in-opencv
    """
    result = cv2.matchTemplate(screenshot, image, cv2.TM_CCOEFF_NORMED)
    w, h = image.shape[:2]
    matching_points = numpy.where(result >= threshold)
    all_matches = zip(*matching_points[::-1])
    # Throwing away all but one match. There could be multiple here.
    try:
        top_left = list(all_matches)[0]
    except IndexError:
        if debug:
            print(f"Couldn't find image {image_name}")
        return None, None
    bottom_right = (top_left[0] + w, top_left[1] + h)
    return top_left, bottom_right


def display_debug_screenshot(screenshot, top, left, refresh_rate_ms=1000, name="Debug", size=(500, 500)):
    """
    params:
        refresh_rate_ms: milliseconds to wait between refresh
    """
    cv2.namedWindow(name, cv2.WINDOW_NORMAL)
    # Move to x, y
    cv2.moveWindow(name, left, top)
    cv2.imshow(name, screenshot)
    cv2.resizeWindow(name, size[0], size[1])
    # Show on top of other windows.
    cv2.setWindowProperty(name, cv2.WND_PROP_TOPMOST, 1)
    cv2.waitKey(delay=int(refresh_rate_ms))


def get_inventory_corner_points(screenshot, debug=False):
    """Takes about 1 full second due to 4x matchTemplate within get_image_on_screen"""
    # Top Left of Inventory
    try:
        top_left_im = cv2.imread("pics/inventory_top_left.png", cv2.IMREAD_COLOR)
        top_left_invent_point, _ = get_image_on_screen(
            screenshot, top_left_im, image_name="inventory_top_left", debug=debug
        )
    except Exception as e:
        if debug:
            print("Couldn't find top_left corner", e)
        top_left_invent_point = None
    # Top Right of Inventory
    try:
        top_right_im = cv2.imread("pics/inventory_top_right.png", cv2.IMREAD_COLOR)
        w, _ = top_right_im.shape[:2]
        top_left, _ = get_image_on_screen(screenshot, top_right_im, image_name="inventory_top_right", debug=debug)
        top_right_invent_point = (top_left[0] + w, top_left[1])
    except Exception as e:
        if debug:
            print("Couldn't find top_right corner", e)
        top_right_invent_point = None
    # Bottom Left of Inventory
    try:
        bottom_left_im = cv2.imread("pics/inventory_bottom_left.png", cv2.IMREAD_COLOR)
        _, h = bottom_left_im.shape[:2]
        top_left, _ = get_image_on_screen(screenshot, bottom_left_im, image_name="inventory_bottom_left", debug=debug)
        bottom_left_invent_point = (top_left[0], top_left[1] + h)
    except Exception as e:
        if debug:
            print("Couldn't find bottom_left corner", e)
        bottom_left_invent_point = None
    # Bottom Right of Inventory
    try:
        bottom_right_im = cv2.imread("pics/inventory_bottom_right.png", cv2.IMREAD_COLOR)
        _, bottom_right_invent_point = get_image_on_screen(
            screenshot, bottom_right_im, image_name="inventory_bottom_right", debug=debug
        )
    except Exception as e:
        if debug:
            print("Couldn't find bottom_right corner", e)
        bottom_right_invent_point = None
    return top_left_invent_point, top_right_invent_point, bottom_left_invent_point, bottom_right_invent_point


def get_inventory_slots(monitor):
    screenshot = get_screenshot_bgr(monitor)
    tl, tr, bl, br = get_inventory_corner_points(screenshot)
    if all([tl, tr, bl, br]):
        return calculate_inventory_slots(tl, tr, bl, br)
    else:
        return None


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


def get_osrs_windows():
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID,
    )

    options = kCGWindowListOptionOnScreenOnly
    windowList = CGWindowListCopyWindowInfo(options, kCGNullWindowID)

    osrs_windows = []
    for window in windowList:
        title = window.get("kCGWindowOwnerName")
        if str(title.lower()) == "runelite":
            osrs_windows.append(window.get("kCGWindowBounds"))

    return osrs_windows
