from pickle import load
from sys import maxsize
import argparse
from typing import Dict
from closest_name import get_closest_runner_name

def get_seconds_from_time_str(timestr: str) -> int:
    spl = timestr.split(":")

    power = len(spl)

    seconds = 0

    for i, val in enumerate(spl):
        seconds += int(val) * 60 ** ((power - 1) - i)

    return seconds


def find_pr(runner: str, distance: int) -> Dict[str, str]:
    with open("./runnerData/{0}.pkl".format(runner), "rb") as f:
        pkl_data = load(f)

        min_sec = maxsize
        min_run_obj = {} # type: Dict[str, str]

        min_date = ""
        for date, runs in pkl_data.items():
            for run in runs.items:
                try:
                    rts = run.time

                    dot_index = rts.index(".")
                    rts = rts[:dot_index]  # Time is structured like (time). (pace per mile).
                    # Removing everything after dot leaves just time

                    run_time = get_seconds_from_time_str(rts)
                    dist = run.distance
                    if dist == distance and run_time != 0 and run_time<min_sec:
                        min_sec = run_time
                        min_run_obj = run
                        min_date = date
                except KeyError as k:
                    pass
        return min_run_obj
