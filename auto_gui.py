import pyautogui
import time
from script_random import random_around, random_point_near_center_of_rect, rsleep


def click(x, y, button="left", time_to_move=(0.15, 0.05)):
    """
    Params:
        x, y: The coordinates to click at.
        button: Which button, left or right, to use to click.
        time_to_move: A tuple of duration and random factor for how long to take to move to x, y.
    """
    if button == "left":
        pyautogui.click(
            x,
            y,
            # Time to move to x, y
            duration=random_around(time_to_move[0], factor=time_to_move[1]),
            button=button,
        )
    elif button == "right":
        # No idea why normal right click isn't working
        # At least on Runelite
        pyautogui.mouseDown(
            x,
            y,
            # Time to move to x, y
            duration=random_around(time_to_move[0], factor=time_to_move[1]),
            button=button,
        )
        pyautogui.mouseUp(button="right")


def press_key(key, hold=0):
    start = time.time()
    pyautogui.press(key)
    while time.time() - start < hold:
        pyautogui.press(key)


def click_in_rect(top_left, bottom_right, clicks=1, wait_between=0, absolute=False):
    """Click in the rectangle, adjusted for screen size difference.

    Params:
        absolute: Whether the coordinates are relative to a screenshot MONITOR or absolute to the screen size.
    """

    x, y = random_point_near_center_of_rect(top_left, bottom_right, absolute=absolute)

    for num in range(clicks):
        if num != 0 and wait_between > 0:
            rsleep(wait_between, factor=0.1)
        click(x, y)
