import time

import numpy
import mss

from colors import BANK_TEXT_COLOR, get_mask
from auto_gui import click
from settings import MONITOR


def get_screenshot():
    with mss.mss() as screenshot:
        return numpy.array(screenshot.grab(MONITOR))


def wait_for_bank():
    inside_bank = False
    while not inside_bank:
        frame = get_screenshot()
        bank_amount_mask = get_mask(frame, BANK_TEXT_COLOR)
        inside_bank = numpy.any(bank_amount_mask)
        time.sleep(0.1)  # Benkmarked at .033 without


def reset_xp_tracker():
    click(825, 325)
    click(825, 325, button="right")
    click(840, 362)
