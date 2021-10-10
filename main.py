from datetime import datetime, timedelta

import time
import pyautogui
import cv2
import numpy
import mss
import random

from colors import GREEN, CYAN, YELLOW, MAGENTA, BANK_TEXT_COLOR, get_mask


MONITOR = {"top": 300, "left": 0, "width": 770, "height": 500}
# numpy_monitor = {"top": 0, "left": 0, "width": 1540, "height": 1000}


def get_rectangle(mask, color_name):
    contours, _ = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 1:
        print(f"Warning! More than one rect for {color_name}")
        return
    x, y, w, h = cv2.boundingRect(contours[0])
    top_left = (x, y)
    bottom_right = (x + w, y + h)
    return (top_left, bottom_right)


def debug_rectangle(image, top_left, bottom_right):
    cv2.rectangle(
        image,
        top_left,
        bottom_right,
        [0, 0, 255],
        2,
    )


def rsleep(seconds, factor=0.2):
    time.sleep(random_around(seconds, factor=factor))


def random_around(num, factor):
    start = num - (num * factor)
    end = num + (num * factor)
    return random.triangular(start, end)


def random_point_near_center_of_rect(top_left, bottom_right):
    CENTER_FACTOR = 4
    width_adjust = (bottom_right[0] - top_left[0]) / CENTER_FACTOR
    height_adjust = (bottom_right[1] - top_left[1]) / CENTER_FACTOR
    left = top_left[0] + width_adjust
    right = bottom_right[0] - width_adjust
    top = top_left[1] + height_adjust
    bottom = bottom_right[1] - height_adjust

    x = round(random.triangular(left, right))
    y = round(random.triangular(top, bottom))

    adjusted_x = (x / 2) - MONITOR["left"]
    adjusted_y = (y / 2) + MONITOR["top"]

    return (adjusted_x, adjusted_y)


def click_in_rect(top_left, bottom_right, clicks=1, wait_between=0):
    """Click in the rectangle, adjusted for screen size difference."""

    x, y = random_point_near_center_of_rect(top_left, bottom_right)

    for num in range(clicks):
        if num != 0 and wait_between > 0:
            rsleep(wait_between, factor=0.1)
        click(x, y)


def click(x, y, button="left"):
    if button == "left":
        pyautogui.click(
            x,
            y,
            # Time to move to x, y
            duration=random_around(0.15, factor=0.05),
            button=button,
        )
    elif button == "right":
        # No idea why normal right click isn't working
        # At least on Runelite
        pyautogui.mouseDown(
            x,
            y,
            # Time to move to x, y
            duration=random_around(0.15, factor=0.05),
            button=button,
        )
        pyautogui.mouseUp(button="right")


def press_key(key, hold=0):
    start = time.time()
    pyautogui.press(key)
    while time.time() - start < hold:
        pyautogui.press(key)


def reset_xp_tracker():
    click(825, 325)
    click(825, 325, button="right")
    click(840, 362)


def wait_for_bank():
    inside_bank = False
    while not inside_bank:
        frame = get_screenshot()
        bank_amount_mask = get_mask(frame, BANK_TEXT_COLOR)
        inside_bank = numpy.any(bank_amount_mask)
        time.sleep(0.1)  # Benkmarked at .033 without


def get_screenshot():
    with mss.mss() as screenshot:
        return numpy.array(screenshot.grab(MONITOR))


def run_for_duration(func, duration):
    count = 0
    start = time.time()
    elapsed = 0

    completed_time = datetime.fromtimestamp(start) + timedelta(seconds=duration)
    print(f"Finished at: {completed_time.strftime('%I:%M:%S%p')}")

    while elapsed < DURATION:
        count += 1
        print(f"Repetition: {count} Elapsed: {round(elapsed/60)}m")
        func()
        elapsed = time.time() - start


if __name__ == "__main__":

    frame = get_screenshot()

    green_mask = get_mask(frame, GREEN)
    green_rect = get_rectangle(green_mask, color_name="green")
    # debug_rectangle(frame, *green_rect)

    cyan_mask = get_mask(frame, CYAN)
    cyan_rect = get_rectangle(cyan_mask, color_name="cyan")
    # debug_rectangle(frame, *cyan_rect)

    yellow_mask = get_mask(frame, YELLOW)
    yellow_rect = get_rectangle(yellow_mask, color_name="yellow")
    # debug_rectangle(frame, *yellow_rect)

    magenta_mask = get_mask(frame, MAGENTA)
    magenta_rect = get_rectangle(magenta_mask, color_name="magenta")
    # debug_rectangle(frame, *magenta_rect)

    def auto_craft():
        # Open the bank
        x, y = random_point_near_center_of_rect(*green_rect)
        click(x, y)
        # Deposit All
        wait_for_bank()
        click(x, y)
        rsleep(0.25)
        # Withdraw all
        click_in_rect(*cyan_rect)
        rsleep(0.25)
        # Esc bank
        press_key("esc")
        rsleep(0.25)
        # Click needle
        click_in_rect(*yellow_rect)
        rsleep(0.3)
        # Click leather
        click_in_rect(*magenta_rect)
        # rsleep(0.7)
        # Make All
        press_key("space", hold=1.25)
        rsleep(18)

    reset_xp_tracker()

    DURATION = 60 * 30
    run_for_duration(auto_craft, DURATION)

    # cv2.waitKey()
