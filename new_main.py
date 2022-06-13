import argparse


def parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--script", "-s", type=str, required=True, help="The script function to run.")
    parser.add_argument("--duration", "-d", type=int, default=0, help="The duration to run `script` in minutes.")
    parser.add_argument(
        "--num-runs", "-n", type=int, default=float("inf"), help="The number of iterations the script should run."
    )

    return parser.parse_args()


if __name__ == "__main__":

    from script_classes.nmz import NMZ

    args = parse_args()

    try:
        c = globals()[args.script]
    except KeyError:
        print(f"\n>>> Couldn't find script '{args.script}' <<<\n")
        print("Make sure name is capitilized correctly and is imported in main.\n")
        print("Found:")
        print(list(s for s in globals().keys() if s[0].isupper()))
        exit()
    script = c(num_runs=args.num_runs, duration=args.duration)
    script.run()
