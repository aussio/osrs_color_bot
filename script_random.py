import time
import random

from settings import MONITOR


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
