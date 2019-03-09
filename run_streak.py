import json
import argparse
from typing import Dict, List, Tuple
from log_classes import LogEntry
from api import SteeplewebAPI
from closest_name import get_closest_runner_name

def find_streak(name: str) -> Tuple[int, List[LogEntry]]:
    with open("./streak_settings.json", "r") as f:
        streak_settings = json.load(f)
    longest_streak_length = 0
    longest_streak = [] # type: List[LogEntry]
    runnerData = SteeplewebAPI.loadRunnerData(name)

    current_streak_length = 0
    current_streak = [] # type: List[LogEntry]
    for date, log_entry in runnerData.items():
        entries = log_entry.items
        if entries == []:
            if current_streak_length > longest_streak_length:
                longest_streak = current_streak
                longest_streak_length = current_streak_length
            current_streak_length = 0
            current_streak = []
            continue
        total_distances = {}
        for activity in entries:
            workout_type = activity.type
            workout_distance = activity.distance
            wc_distance = activity.warmup_cooldown
            distance = workout_distance + wc_distance
            if workout_type not in total_distances.keys():
                total_distances[workout_type] = distance
            else:
                total_distances[workout_type] += distance
        activity_counts_toward_streak = False
        for workout_type, distance_worked_out in total_distances.items():
            if workout_type in streak_settings and distance_worked_out >= float(streak_settings[workout_type]):
                activity_counts_toward_streak = True

        if "Total" in streak_settings and sum(total_distances.values()) >= float(streak_settings["Total"]):
            activity_counts_toward_streak = True
        
        if activity_counts_toward_streak:
            current_streak_length += 1
            current_streak.append(log_entry)
        else:
            if current_streak_length > longest_streak_length:
                longest_streak = current_streak
                longest_streak_length = current_streak_length
            current_streak_length = 0
            current_streak = []
    return (longest_streak_length, longest_streak)

def all_runners_streaks() -> Dict[str, int]:
    runners = []
    with open("./runnerData/runners.txt", "r") as f:
        for line in f.readlines():
            runner = line.split(",")[0]
            runners.append(runner)

    streaks = {}
    for runner in runners:
        streak, _ = find_streak(runner)
        streaks[runner] = streak

    return streaks

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description="Find PR's of various distances"
    )

    parser.add_argument(
            "runner",
            type=str,
            help="Name of runner"
    )

    args = parser.parse_args()
    runner = get_closest_runner_name(args.runner)
    streak, _ = find_streak(runner)
    runner = runner.strip()
    print(f"{runner}'s longest running streak was {streak} days!")
