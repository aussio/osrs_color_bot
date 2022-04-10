import argparse
from math import inf
import time
import cv2
from datetime import datetime, timedelta

from colors import GREEN, CYAN, DARK_CYAN, ORANGE, YELLOW, MAGENTA, get_mask
from script_classes.construction import Construction
from script_classes.mining import Mining
from script_random import random_around, rsleep
from script_utils import get_rectangle, get_screenshot, reset_xp_tracker
from scripts import auto_craft, auto_cast_superglass, Fishing, smith_platebodies_varrock


def debug_rectangle(image, top_left, bottom_right):
    cv2.rectangle(
        image,
        top_left,
        bottom_right,
        [0, 0, 255],
        2,
    )


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
        "--num-runs", "-n", type=int, default=999999, help="The number of iterations the script should run."
    )
    parser.add_argument("--lag", type=float, default=1, help="Lag factor. Multiplies select sleep times.")
    parser.add_argument(
        "--reset-xp", "-r", action="store_true", default=False, help="If passed, reset the Runelite xp tracker."
    )
    parser.add_argument("--start", type=int, default=0, help="If passed, what stage in the script to start.")

    return parser.parse_args()


def get_color_rect(color, debug=False):
    mask = get_mask(frame, color)
    rect = get_rectangle(mask, color_name=color)
    if debug:
        debug_rectangle(frame, *rect)
    return rect


if __name__ == "__main__":

    frame = get_screenshot()

    args = parse_args()

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

    # def clean():
    #     clean_herbs()

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
