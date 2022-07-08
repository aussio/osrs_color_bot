import argparse
import time
from datetime import datetime, timedelta

import cv2
import pytesseract
from auto_gui import slow_click

from colors import GREEN, CYAN, DARK_CYAN, ORANGE, YELLOW, MAGENTA, get_mask
from script_classes.old_style.construction import Construction
from script_classes.old_style.mining import Mining
from script_classes.old_style.woodcutting import Woodcutting
from script_classes.old_style.zach_woodcut import ZachWoodcutting
from script_random import random_around, rsleep
from script_utils import (
    debug_points_on_screen,
    debug_rectangle,
    display_debug_screenshot,
    get_image_on_screen,
    get_inventory_slots,
    get_rectangle,
    get_screenshot,
    reset_xp_tracker,
)
from scripts import auto_craft, Fishing, clean_herbs, smith_platebodies_varrock, auto_cast_plankmake
from settings import BOTTOM_LEFT_WINDOW


DEFAULT_NUM_RUNS = 999999
DEFAULT_SLEEP = 30


def run_for_duration(func, duration, num_runs, sleep_after_count):
    """
    Args:
        sleep_after_count (int, int): Tuple of (count to sleep at, time to sleep)
    """
    count = 0
    start = time.time()
    elapsed = 0
    if sleep_after_count:
        sleep_after_count_random = randomize_sleep_after_count(sleep_after_count[0])
        print(f"First sleep_after_count: {sleep_after_count_random} for {sleep_after_count[1]} seconds")

    completed_time = datetime.fromtimestamp(start) + timedelta(seconds=duration)
    print(f"Starting {func.__name__}. Will finish at: {completed_time.strftime('%I:%M:%S%p')}")

    while elapsed < DURATION and count < num_runs:
        count += 1
        if count % 10 == 0:
            print(f"Repetition: {count} Elapsed: {round(elapsed/60)}m")

        func()

        elapsed = time.time() - start
        if sleep_after_count and count % sleep_after_count_random == 0:
            print(f"sleep_after_count: {sleep_after_count_random} for {sleep_after_count[1]} seconds'ish")
            rsleep(sleep_after_count[1], factor=0.5)
            sleep_after_count_random = sleep_after_count_random + randomize_sleep_after_count(sleep_after_count[0])


def randomize_sleep_after_count(count):
    return int(random_around(count, 0.5))


def parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--script", "-s", type=str, required=True, help="The script function to run.")
    parser.add_argument("--duration", "-d", type=int, default=30, help="The duration to run `script` in minutes.")
    parser.add_argument(
        "--num-runs", "-n", type=int, default=DEFAULT_NUM_RUNS, help="The number of iterations the script should run."
    )
    parser.add_argument("--lag", type=float, default=1, help="Lag factor. Multiplies select sleep times.")
    parser.add_argument(
        "--reset-xp", "-r", action="store_true", default=False, help="If passed, reset the Runelite xp tracker."
    )
    parser.add_argument("--start", type=int, default=0, help="If passed, what stage in the script to start.")
    # Used by autoclicker
    parser.add_argument(
        "--sleep", type=int, default=DEFAULT_SLEEP, help="How long the script should sleep between iterations."
    )
    parser.add_argument("--clicks", type=int, default=1, help="")

    return parser.parse_args()


def get_color_rect(color, debug=False):
    mask = get_mask(frame, color)
    rect = get_rectangle(mask, color_name=color)
    if rect is None:
        print("No rect of color: {}".format(color))
    if debug:
        debug_rectangle(frame, rect[0], rect[1])
    return rect


if __name__ == "__main__":

    frame = get_screenshot()
    args = parse_args()

    def autoclick():
        # WARNING: CAREFUL USING THIS! EASILY BANNABLE
        # Got the hard-coded coordinates from the Mac screenshot util
        x = 572
        y = 538

        sleep_time = args.sleep
        # click_times = round(random_around(args.clicks, 0.33))
        click_times = 1

        print(f"Clicking {click_times} times per {sleep_time} seconds.")

        x = random_around(x, 0.005)
        y = random_around(y, 0.005)
        for _ in range(click_times):
            slow_click(x, y)
            rsleep(0.1)

        rsleep(sleep_time, 0.1)

    def debug():
        # Take screenshot
        frame = get_screenshot(BOTTOM_LEFT_WINDOW)
        inventory_slot_points = get_inventory_slots(BOTTOM_LEFT_WINDOW)
        if inventory_slot_points:
            debug_points_on_screen(frame, inventory_slot_points)
        display_debug_screenshot(frame, BOTTOM_LEFT_WINDOW, refresh_rate_ms=200)

    def debug_status_bar_simple():
        # get image in grayscale
        for hp_img in [
            # cv2.imread("pics/hp_status_bar.png", cv2.IMREAD_GRAYSCALE),
            # cv2.imread("pics/hp_status_bar_hard.png", cv2.IMREAD_GRAYSCALE),
            cv2.imread("pics/prayer_status_bar.png", cv2.IMREAD_GRAYSCALE),
        ]:
            # Get only the pure white values
            bw_text_only = cv2.threshold(hp_img, 250, 255, cv2.THRESH_BINARY)[1]
            # Invert to be white background with black text
            bw_text_only = cv2.bitwise_not(bw_text_only)
            cv2.imshow("HP", bw_text_only)

            seven = cv2.imread("pics/7.png", cv2.IMREAD_GRAYSCALE)
            bw_text_only_num_1 = cv2.threshold(seven, 250, 255, cv2.THRESH_BINARY)[1]
            # Invert to be white background with black text
            bw_text_only_num_1 = cv2.bitwise_not(bw_text_only_num_1)
            # cv2.imshow("HP", seven)

            tl, br = get_image_on_screen(bw_text_only, seven, threshold=0.5)
            print(tl, br)

            cv2.waitKey(delay=2000)
            cv2.destroyAllWindows()

    def debug_status_bar():
        # get image in grayscale
        for hp_img in [
            cv2.imread("pics/hp_status_bar.png", cv2.IMREAD_GRAYSCALE),
            cv2.imread("pics/hp_status_bar_hard.png", cv2.IMREAD_GRAYSCALE),
            cv2.imread("pics/prayer_status_bar.png", cv2.IMREAD_GRAYSCALE),
        ]:
            # Get only the pure white values
            white_text_only = cv2.threshold(hp_img, 250, 255, cv2.THRESH_BINARY)[1]
            # Invert to be white background with black text
            black_text_only = cv2.bitwise_not(white_text_only)
            # Zoom in to make text thicker
            zoom_img = cv2.resize(black_text_only, None, fx=5, fy=5)

            # Blur the image to *really* make the text thicker
            blur_img = zoom_img

            blur_img = cv2.medianBlur(blur_img, ksize=11)
            # blur_img = cv2.boxFilter(blur_img, -1, (7, 7))
            # blur_img = cv2.blur(blur_img, (7, 7))
            # blur_img = cv2.GaussianBlur(blur_img, (zoom, zoom), 0)
            # Clean up zoomed image to be pure black-white for tesseract instead of blurry grey
            blurred_bw_img = cv2.threshold(blur_img, 150, 255, cv2.THRESH_BINARY)[1]

            cv2.imshow("HP", blurred_bw_img)
            print(
                pytesseract.image_to_string(blurred_bw_img, config="--psm 6 -c tessedit_char_whitelist=0123456789"),
                end="",
            )

            cv2.waitKey(delay=1000)
            cv2.destroyAllWindows()

    def woodcut():
        w = ZachWoodcutting(tree_highlight_color=YELLOW)
        w.chop()

    def dhide():
        auto_craft(
            bank_rect=get_color_rect(GREEN),
            withdraw1_rect=get_color_rect(CYAN),
            item1_rect=get_color_rect(YELLOW),
            item2_rect=get_color_rect(MAGENTA),
            wait_time=18,
            lag_factor=args.lag,
        )

    def potions():
        auto_craft(
            bank_rect=get_color_rect(GREEN),
            withdraw1_rect=get_color_rect(CYAN),
            withdraw2_rect=get_color_rect(DARK_CYAN),
            item1_rect=get_color_rect(YELLOW),
            item2_rect=get_color_rect(MAGENTA),
            wait_time=18,
            lag_factor=args.lag,
        )

    def stringbows():
        auto_craft(
            bank_rect=get_color_rect(GREEN),
            withdraw1_rect=get_color_rect(CYAN),
            withdraw2_rect=get_color_rect(DARK_CYAN),
            item1_rect=get_color_rect(YELLOW),
            item2_rect=get_color_rect(MAGENTA),
            wait_time=18,
            lag_factor=args.lag,
        )

    def wine():
        auto_craft(
            bank_rect=get_color_rect(GREEN),
            withdraw1_rect=get_color_rect(CYAN),
            withdraw2_rect=get_color_rect(DARK_CYAN),
            item1_rect=get_color_rect(YELLOW),
            item2_rect=get_color_rect(MAGENTA),
            wait_time=20,
            lag_factor=args.lag,
        )

    # def superglass():
    #     auto_cast_superglass(
    #         bank_rect=green_rect,
    #         withdraw1_rect=cyan_rect,
    #         withdraw2_rect=dark_cyan_rect,
    #         cast_spell_rect=yellow_rect,
    #     )

    def plankmake():
        auto_cast_plankmake(
            bank_rect=get_color_rect(GREEN),
            withdraw1_rect=get_color_rect(DARK_CYAN),
            cast_spell_rect=get_color_rect(MAGENTA),
        )

    def platebody():
        smith_platebodies_varrock(
            bank_booth_color=MAGENTA,
            deposit_all=get_color_rect(GREEN),
            withdraw=get_color_rect(CYAN),
            anvil=get_color_rect(YELLOW),
            platebody=get_color_rect(DARK_CYAN),
            start=args.start,
        )

    def fishing():
        Fishing.barbarian_fishing(
            fishing_rect_color=MAGENTA,
        )

    def woodcutting():
        w = Woodcutting(tree_rect_color=GREEN, special_attack_color=MAGENTA)
        w.blisterwood()

    MINING_SLEEP_AFTER_COUNT = (30, 5)

    def mining():
        m = Mining(
            iron_1=get_color_rect(GREEN),
            iron_2=get_color_rect(DARK_CYAN),
            iron_3=get_color_rect(CYAN),
            inventory_1=get_color_rect(YELLOW),
            inventory_2=get_color_rect(MAGENTA),
            inventory_3=get_color_rect(ORANGE),
        )
        m.mine_iron()

    CONSTRUCTION_SLEEP_AFTER_COUNT = (20, 5)

    def construction():
        # Does get re-run every time, so class knows how to set itself
        # into the proper state each run.
        c = Construction(
            clickbox_rect_color=GREEN,
            butler_color=MAGENTA,
        )
        c.oak_larders()

    def clean():
        clean_herbs(
            bank_rect=get_color_rect(GREEN),
            withdraw1_rect=get_color_rect(CYAN),
        )

    # Set sleep_after_count
    if args.script == "mining":
        sleep_after_count = MINING_SLEEP_AFTER_COUNT
    elif args.script == "construction":
        sleep_after_count = CONSTRUCTION_SLEEP_AFTER_COUNT
    else:
        sleep_after_count = None

    if args.reset_xp:
        reset_xp_tracker()
    DURATION = 60 * args.duration
    try:
        run_for_duration(locals()[args.script], DURATION, args.num_runs, sleep_after_count)
    except KeyError:
        print(f"Could not find script {args.script}.")
    except KeyboardInterrupt:
        print("Script quit!")

    # cv2.waitKey()
