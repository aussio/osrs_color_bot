"""
This would make the most sense to be user settings in a GUI or similar.
For now, this is essentially just a "constants" file.
"""

from colors import SOLID_GREEN


# MONITOR = {"top": 284, "left": 0, "width": 770, "height": 500}
MONITOR = {"top": 0, "left": 0, "width": 1120, "height": 1059}
BOTTOM_LEFT_WINDOW = {"top": 540, "left": 0, "width": 770, "height": 505}
FISHING_STATUS = {"top": 300, "left": 0, "width": 140, "height": 80}
# This is intended to be where the player currently is, since they are usually
# always at the center of the screen. (x, y)
CENTER_OF_SCREEN_ABSOLUTE = (385, 550)
CENTER_OF_SCREEN_RELATIVE = (385, 550)

INVENTORY_SLOT_RECTS_ABSOLUTE = [
    # Row 1
    ((595, 475), (615, 494)),
    ((635, 475), (658, 494)),
    ((675, 475), (700, 494)),
    ((715, 475), (740, 494)),
    # Row 2
    ((595, 510), (615, 530)),
    ((635, 510), (658, 530)),
    ((675, 510), (700, 530)),
    ((715, 510), (740, 530)),
    # Row 3
    ((595, 545), (615, 565)),
    ((635, 545), (658, 565)),
    ((675, 545), (700, 565)),
    ((715, 545), (740, 565)),
    # Row 4
    ((595, 575), (615, 605)),
    ((635, 575), (658, 605)),
    ((675, 575), (700, 605)),
    ((715, 575), (740, 605)),
    # Row 5
    ((595, 615), (615, 640)),
    ((635, 615), (658, 640)),
    ((675, 615), (700, 640)),
    ((715, 615), (740, 640)),
    # Row 6
    ((595, 650), (615, 675)),
    ((635, 650), (658, 675)),
    ((675, 650), (700, 675)),
    ((715, 650), (740, 675)),
    # Row 7
    ((595, 690), (615, 710)),
    ((635, 690), (658, 710)),
    ((675, 690), (700, 710)),
    ((715, 690), (740, 710)),
]

# [
# 1, 2, 3, 4,
# 5, 6, 7, 8,
# 9, 10, 11, 12,
# 13, 14, 15, 16,
# 17, 18, 19, 20,
# 21, 22, 23, 24,
# 25, 26, 27, 28
# ]

FISHING_DROP_ORDER = [4, 3, 7, 8, 12, 11, 15, 16, 20, 19, 23, 24, 28, 27, 26, 25, 21, 22, 18, 17, 13, 14, 10, 9, 5, 6]

CLEAN_CLICK_ORDER = [
    4,
    3,
    7,
    8,
    12,
    11,
    15,
    16,
    20,
    19,
    23,
    24,
    28,
    27,
    26,
    25,
    21,
    22,
    18,
    17,
    13,
    14,
    10,
    9,
    5,
    6,
    2,
    1,
]

WOODCUTTING_DROP_ORDER = CLEAN_CLICK_ORDER

DEBUG = False

# Special attack recharges every 5 minutes.
SPECIAL_ATTACK_RECHARGE_SECONDS = 300

# HP and Prayer colors
# It looks like they go from solid green to solid yellow to solid red
# with a completely smooth transition between them.
# Some RGB square roots for distance seem conventional: https://en.wikipedia.org/wiki/Color_difference#Euclidean
# Then from there, do a mask on that light brown (background) and black (shadow)
# to be left with only the color. Do a distance, and you'll know roughly where you're at.
max = 255
FULL = [0, max, 0]  # SOLID GREEN
THREE_QUARTER = [max / 2, max, 0]
HALF = [max, max, 0]  # SOLID YELLOW
ONE_QUARTER = [max, max / 2, 0]
EMPTY = [max, 0, 0]  # SOLID RED
