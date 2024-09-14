import pyautogui
import time
from script_random import random_around, random_point_near_center_of_rect, rsleep


def slow_click(x, y, button="left"):
    """
    Various entities won't regularly register clicks when the mouse teleports and clicks on them.
    Something about separating these two actions causes the clicks to always register.
    """
    pyautogui.moveTo(x, y)
    click(x, y, button=button, time_to_move=(0, 0))


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


def press_key(key, hold=0, factor=0.1):
    hold = random_around(hold, factor)
    start = time.time()
    pyautogui.press(key)
    while time.time() - start < hold:
        pyautogui.press(key)


def click_in_rect(top_left, bottom_right, clicks=1, wait_between=0, absolute=False, delay=0):
    """Click in the rectangle, adjusted for screen size difference.

    Params:
        absolute: Whether the coordinates are relative to a screenshot MONITOR or absolute to the screen size.
    """
    if delay > 0:
        rsleep(delay)

    x, y = random_point_near_center_of_rect(top_left, bottom_right, absolute=absolute)

    for num in range(clicks):
        if num != 0 and wait_between > 0:
            rsleep(wait_between, factor=0.1)
        click(x, y)
