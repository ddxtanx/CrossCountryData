from PyInquirer import prompt, print_json
from api import SteeplewebAPI, get_login_data, write_login_data
from closest_name import get_closest_runner_name
from find_pr import find_pr
from run_streak import find_streak, all_runners_streaks
from operator import itemgetter
from typing import Dict, List
import requests
import getpass
import datetime
import json


def option_question_constructor(name: str) -> Dict[str, str]:
    tense_dict = {
        "Bike": "biking",
        "Run": "running",
        "Swim": "swimming",
        "Walk": "walking"
    }
    present_progressive = tense_dict[name]
    return {
            "type": "input",
            "name": name,
            "message": "What is the minimum {0} distance (in miles) needed to count towards a streak?".format(
                present_progressive
            )
        }
if __name__ == "__main__":
    q1 = [
        {
            "type": "rawlist",
            "name": "action",
            "message": "What would you like to do?",
            "choices": [
                "Download data.",
                "Find PR's.",
                "Find a runner's longest running streak.",
                "View streak leaderboard."
            ]
        }
    ]

    q2_download_1 = [
        {
            "type": "input",
            "name": "start_date",
            "message": "Starting at what date? (M-D-Y)"
        },
        {
            "type": "input",
            "name": "end_date",
            "message": "Ending at what date? (M-D-Y)"
        },
        {
            "type": "confirm",
            "name": "overwrite",
            "message": "Would you like to overwrite days that were previously downloaded?"
        },
        {
            "type": "confirm",
            "name": "specific",
            "message": "Would you like to get data from a specific person?"
        }
    ]

    q2_download_2 = [
        {
            "type": "input",
            "name": "person",
            "message": "Whose data would you like to get?"
        }
    ]

    q2_find_prs = [
        {
            "type": "input",
            "name": "person",
            "message": "Whose PR would you like to get?"
        },
        {
            "type": "input",
            "name": "distance",
            "message": "What distance?"
        }
    ]

    with open("./streak_settings.json", "r") as f:
        current_settings = json.load(f)

    settings_keys = list(current_settings.keys())

    activities = ["Run", "Bike", "Walk", "Swim"]
    q2_streak_settings_choices = []
    for activity in activities:
        choice = {"name": activity}
        if activity in settings_keys:
            choice["checked"] = True
        q2_streak_settings_choices.append(choice)
    q2_streak = [
        {
            "type": "input",
            "name": "person",
            "message": "Whose longest streak would you like to get?"
        },
        {
            "type": "confirm",
            "name": "view",
            "message": "Would you like to see the start and end date of the streak?"
        },
        {
            "type": "confirm",
            "name": "options",
            "message": (
                "Would you like to change what kinds of activities are counted in streaks?"
            )
        }
    ]

    q2_streak_opt_1 = {
        "type": "rawlist",
        "name": "criteria",
        "message": "How would you like to count activities?",
        "choices": [
            "Minimum distance for each specific activity.",
            "Minumum distance over all activities logged in a day."
        ]
    }
    q2_streak_opt_2_1 = [
        {
            "type": "checkbox",
            "name": "types",
            "message": "What type of activity should count towards a streak?",
            "choices": q2_streak_settings_choices
        }
    ]

    q2_streak_opt_2_2 = [
        {
            "type": "input",
            "name": "Total",
            "message": "What should the minimum distance (in miles) be?"
        }
    ]

    empty_obj = {
        "username": "",
        "password": ""
    }
    username = ""
    password = ""
    cookie = ""
    user_data = get_login_data()
    while cookie == "":
        if username != "":
            user_data = {}
            print("Login failed, please try again.")
        if user_data == empty_obj:
            username = input("Steepleweb Username: ")
            password = getpass.getpass("Steepleweb Password: ")
        else:
            username = user_data["username"]
            password = user_data["password"]
        data = {
            "myusername": username,
            "mypassword": password,
            "remember": "TRUE"
        }

        r = requests.post(
                        "https://www.steepleweb.com/teams/oprfxc/login/checklogin.php",
                        data=data
        )

        cookie = r.history[0].cookies["sw1163"]
    api = SteeplewebAPI(cookie)
    write_login_data({
        "username": username,
        "password": password
    })
    answer1 = prompt(q1)

    if answer1["action"] == "Download data.":
        prelim_data = prompt(q2_download_1)
        start_date = datetime.datetime.strptime(prelim_data["start_date"], "%m-%d-%Y")
        end_date = datetime.datetime.strptime(prelim_data["end_date"], "%m-%d-%Y")
        dates = [
                    (start_date + datetime.timedelta(days=x)).strftime("%m/%d/%Y")
                    for x in range(0, (end_date-start_date).days + 1)
        ]
        runners = api.getRunners()
        if not prelim_data["specific"]:
            c = 0
            for runner, rid in runners.items():
                c += 1
                api.writeRunnerData(runner, rid, dates, prelim_data["overwrite"])
                print("\n{0}/{1} runners completed".format(c, len(runners)))
        else:
            extra_data = prompt(q2_download_2)
            runner = extra_data["person"]
            closest_name = get_closest_runner_name(runner)
            closest_id = runners[closest_name]
            api.writeRunnerData(runner, closest_id, dates, prelim_data["overwrite"])
    elif answer1["action"] == "Find PR's.":
        pr_details = prompt(q2_find_prs)
        runner = get_closest_runner_name(pr_details["person"])
        distance = int(pr_details["distance"])
        pr_details = find_pr(runner, distance)

        if pr_details.date != "":
            print("{0}'s fastest {1} mile time was {2} on {3}".format(
            runner,
            distance,
            pr_details.time,
            pr_details.date
        ))
        else:
            print("{0} never logged a timed {1} mile run...".format(runner, distance))
    elif answer1["action"] == "Find a runner's longest running streak.":
        streak_details = prompt(q2_streak)
        runner = get_closest_runner_name(streak_details["person"])
        if streak_details["options"]:
            type_of_settings = prompt(q2_streak_opt_1)
            if "Minimum distance for each specific activity." in type_of_settings:
                counted_activities = prompt(q2_streak_opt_2_1)["types"]
                dist_questions = list(
                    map(
                        option_question_constructor,
                        counted_activities
                    )
                )
                dist_answers = prompt(dist_questions)
                with open("./streak_settings.json", "w") as f:
                    json.dump(dist_answers, f)
            else:
                min_dist = prompt(q2_streak_opt_2_2)
                with open("./streak_settings.json", "w") as f:
                    json.dump(min_dist, f)
        streak_len, streak = find_streak(runner)
        runner = runner.strip()
        print(f"{runner}'s longest running streak was {streak_len} days!")
        if streak_details["view"]:
            start = streak[0].items[0].date
            end = streak[-1].items[0].date
            print(f"The streak began on {start} and ended on {end}")
    else:
        streak_data = all_runners_streaks()
        sorted_streaks = sorted(
            streak_data.items(),
            key = itemgetter(1)
        )
        for runner, streak_len in sorted_streaks:
            print(f"{runner}: {streak_len}")
