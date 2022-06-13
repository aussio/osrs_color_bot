from auto_gui import slow_click
from script_random import random_point_near_center_of_rect, rsleep


class Mining:
    SLEEP_BETWEEN_ROCKS = 1.55

    def __init__(
        self,
        iron_1,
        iron_2,
        iron_3,
        inventory_1,
        inventory_2,
        inventory_3,
    ):
        self.iron_1 = iron_1
        self.iron_2 = iron_2
        self.iron_3 = iron_3
        self.inventory_1 = inventory_1
        self.inventory_2 = inventory_2
        self.inventory_3 = inventory_3

    def mine_iron(self):

        self.slow_click_center_rect(self.iron_1)
        rsleep(self.SLEEP_BETWEEN_ROCKS, 0.05)
        self.slow_click_center_rect(self.iron_2)
        rsleep(self.SLEEP_BETWEEN_ROCKS, 0.05)

        self.slow_click_center_rect(self.inventory_1)
        self.slow_click_center_rect(self.inventory_2)
        self.slow_click_center_rect(self.inventory_3)

        self.slow_click_center_rect(self.iron_3)
        rsleep(self.SLEEP_BETWEEN_ROCKS, 0.05)

    def slow_click_center_rect(self, rect):
        x, y = random_point_near_center_of_rect(*rect)
        slow_click(x, y)
