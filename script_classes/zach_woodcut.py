import numpy
from auto_gui import slow_click
from colors import SOLID_GREEN, get_mask
from script_random import random_point_near_center_of_rect, rsleep
from script_utils import get_closest_rectangle_to_center, get_screenshot
from settings import FISHING_STATUS


class ZachWoodcutting:
    def __init__(self, tree_highlight_color):
        self.tree_color = tree_highlight_color

    def is_chopping(self):
        frame = get_screenshot(monitor=FISHING_STATUS)
        status_mask = get_mask(frame, SOLID_GREEN)
        is_actively_chopping = numpy.any(status_mask)
        return is_actively_chopping

    def chop(self):
        if self.is_chopping():
            print("Woodcutting")
        else:
            print("Idle")

            rect = get_closest_rectangle_to_center(color=self.tree_color)

            if rect:
                x, y = random_point_near_center_of_rect(*rect)
                slow_click(x, y)

        rsleep(3)
