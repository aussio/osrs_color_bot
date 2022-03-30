import argparse
from math import inf
import time
import cv2
from datetime import datetime, timedelta

from colors import GREEN, CYAN, DARK_CYAN, YELLOW, MAGENTA, get_mask
from script_classes.construction import Construction
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


def run_for_duration(func, duration, num_runs):
    count = 0
    start = time.time()
    elapsed = 0

    completed_time = datetime.fromtimestamp(start) + timedelta(seconds=duration)
    print(f"Starting {func.__name__}. Will finish at: {completed_time.strftime('%I:%M:%S%p')}")

    while elapsed < DURATION and count < num_runs:
        count += 1
        if count % 10 == 0:
            print(f"Repetition: {count} Elapsed: {round(elapsed/60)}m")
        func()
        elapsed = time.time() - start


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


if __name__ == "__main__":

    frame = get_screenshot()

    # green_mask = get_mask(frame, GREEN)
    # green_rect = get_rectangle(green_mask, color_name="green")
    # debug_rectangle(frame, *green_rect)

    # cyan_mask = get_mask(frame, CYAN)
    # cyan_rect = get_rectangle(cyan_mask, color_name="cyan")
    # debug_rectangle(frame, *cyan_rect)

    # dark_cyan_mask = get_mask(frame, DARK_CYAN)
    # dark_cyan_rect = get_rectangle(dark_cyan_mask, color_name="dark_cyan")
    # debug_rectangle(frame, *dark_cyan_mask)

    # yellow_mask = get_mask(frame, YELLOW)
    # yellow_rect = get_rectangle(yellow_mask, color_name="yellow")
    # debug_rectangle(frame, *yellow_rect)

    # magenta_mask = get_mask(frame, MAGENTA)
    # magenta_rect = get_rectangle(magenta_mask, color_name="magenta")
    # debug_rectangle(frame, *magenta_rect)

    args = parse_args()

    def dhide():
        auto_craft(
            bank_rect=green_rect,
            withdraw1_rect=cyan_rect,
            item1_rect=yellow_rect,
            item2_rect=magenta_rect,
            wait_time=18,
            lag_factor=args.lag,
        )

    def potions():
        auto_craft(
            bank_rect=green_rect,
            withdraw1_rect=cyan_rect,
            withdraw2_rect=dark_cyan_rect,
            item1_rect=yellow_rect,
            item2_rect=magenta_rect,
            wait_time=18,
            lag_factor=args.lag,
        )

    def stringbows():
        auto_craft(
            bank_rect=green_rect,
            withdraw1_rect=cyan_rect,
            withdraw2_rect=dark_cyan_rect,
            item1_rect=yellow_rect,
            item2_rect=magenta_rect,
            wait_time=18,
            lag_factor=args.lag,
        )

    def wine():
        auto_c11111111raft(
            bank_rect=green_rect,
            withdraw1_rect=cyan_rect,
            withdraw2_rect=dark_cyan_rect,
            item1_rect=yellow_rect,
            item2_rect=magenta_rect,
            wait_time=20,
            lag_factor=args.lag,
        )

    def superglass():
        auto_cast_superglass(
            bank_rect=green_rect,
            withdraw1_rect=cyan_rect,
            withdraw2_rect=dark_cyan_rect,
            cast_spell_rect=yellow_rect,
        )

    def platebody():
        smith_platebodies_varrock(
            bank_booth_color=MAGENTA,
            deposit_all=green_rect,
            withdraw=cyan_rect,
            anvil=yellow_rect,
            platebody=dark_cyan_rect,
            start=args.start,
        )

    def fishing():
        Fishing.barbarian_fishing(
            fishing_rect_color=MAGENTA,
        )

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

    if args.reset_xp:
        reset_xp_tracker()
    DURATION = 60 * args.duration
    try:
        run_for_duration(locals()[args.script], DURATION, args.num_runs)
    except KeyError:
        print(f"Could not find script {args.script}.")
    except KeyboardInterrupt:
        print("Script quit!")

    # cv2.waitKey()
