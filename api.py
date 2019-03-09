import requests
import pickle
import json
import datetime
import sys
import argparse
from typing import Dict, List
from bs4 import BeautifulSoup as BS
import getpass
import os
from log_classes import LogItem, LogEntry
cookie = ""

def get_login_data() -> Dict[str, str]:
    with open("./conf.json", "r") as f:
        return json.loads(f.read())

def write_login_data(loginData: Dict[str, str]) -> None:
    with open("./conf.json", "w") as f:
        json.dump(loginData, f, sort_keys=True, indent=4, separators=(',', ': '))

class SteeplewebAPI():
    def __init__(self, cookie: str) -> None:
        self.cookie = cookie
    def getRunners(self) -> Dict[str, str]:
        """Gets all runners and their runner ids.

        Returns
        -------
        Dict[str, str]
            A dictionary where the first key is the runner's name
            and the second key is the runner's runner id in
            steepleweb.

        """
        runners = {}

        r = requests.get(
                    "https://www.steepleweb.com/teams/oprfxc/log/training_log.php",
                    cookies={
                        "sw1163": self.cookie
                    }
        )

        soup = BS(r.text, "html.parser")
        for element in soup.find(id="user_list_11").children:
            name = element.text
            url = element.contents[0]["href"]
            rid = url.replace("index.php?user=", "")
            runners[name] = rid
        return runners

    def getDataFromDay(self, date: str, runner: str, rid: str) -> LogEntry:
        """Get's a runners log from a given day.

        Parameters
        ----------
        date : str
            A day in 'M/D/Y' format.
        runner : str
            Name of the runner.
        rid : str
            The runner's runner id.

        Returns
        -------
        LogEntry
            List of workouts the runner logged on that day.

        Raises
        -------
        AttributeError
            Raised if runner has no log on a given day.

        """
        url = "https://www.steepleweb.com/teams/oprfxc/log/view_day.php?date={0}&user={1}".format(
            date,
            rid
        )
        try:
            r = requests.get(url, cookies={
                "sw1163": self.cookie
            })
        except requests.exceptions.ConnectionError:
            print("Runner {0} failed on date {1}, please retry after.".format(runner, date))
            return LogEntry([])

        text = r.text.replace("\n", "")
        text = text.replace("<legend>Log Info</legend>", "")
        text = text.replace("<legend>Extra Info</legend>", "")
        text = text.replace("<legend>Notes</legend>", "")
        text = text.replace("<dt><strong>Time:</strong></dd>",
                            "<dt><strong>Time:</strong></dt>")
        soup = BS(text, "html.parser")
        try:
            logColumn1 = soup.find_all(class_="log_col1")
            logColumn2 = soup.find_all(class_="log_col2")
            contents1 = [l.contents[1] for l in logColumn1]
            contents2 = [l.contents[1] for l in logColumn2]
            logContents = [
                            l1.contents + l2.contents
                            for l1, l2 in zip(contents1, contents2)
            ]
            count = 0
        except AttributeError as e:
            print(e)
            print("Nothing on {0} for {1}".format(date, runner))
            pass
        days = []
        for log in logContents:
            dayData = {}
            try:
                exerName = soup.find_all("legend")[count].get_text().split("-")[0]
                exerType = exerName.split(":")[0]
                exerTitle = exerName.split(":")[1].strip()
                dayData["type"] = exerType
                dayData["title"] = exerTitle
                count += 1
            except AttributeError as e:
                print(soup.find_all("legend")[count].get_text())
                raise e
            for element in log:
                if element.name == "dl" or element.name == "dd":
                    dataName = element.contents[1].get_text()
                    try:
                        dataValue = element.contents[3].get_text().replace(
                            "\u00a0",
                            ""
                        )
                    except Exception as e:
                        dataValue = ""
                    dataName = dataName.replace(":", "")
                    dayData[dataName] = dataValue
            day_log_item = LogItem(
                date,
                dayData["type"],
                dayData["title"],
                dayData["Time of Day"],
                dayData["Route"],
                dayData["Distance"],
                dayData["Time"],
                dayData["Shoes"],
                dayData["Warmup/Cooldown Miles"] if "Warmup/Cooldown Miles" in dayData.keys() else "0 miles",
                dayData["Temperature"],
                dayData["Conditions"],
                dayData["Wind"],
                dayData["Hours of Sleep Last Night"] if "Hourse Of Sleep Last Night" in dayData.keys() else "0 hours"
            )
            days.append(day_log_item)
        entry = LogEntry(days)
        return entry


    def getRunnerData(
        self,
        runner: str,
        rid: str,
        dates: List[str],
        override: bool = False
    ) -> Dict[str, LogEntry]:
        """Get runner data throught a given list of dates.

        Parameters
        ----------
        runner : str
            Name of the runner.
        rid : str
            Runner's runner id.
        dates : List[str]
            List of dates in "M/D/Y" format.

        Returns
        -------
        Dict[str, LogEntry]
            A dictionary where the key is a date, and the values is a
            list of workouts the runner logged on a given day.

        Raises
        -------
        None

        """
        userLog = {}
        current_data = self.loadRunnerData(runner)
        for i, date in enumerate(dates):
            print(
                "\r Downloading {0}'s data: {1}/{2} days completed".format(
                    runner,
                    i+1,
                    len(dates)
                ),
                end=""
            )
            datetimeObj = datetime.datetime.strptime(date, "%m/%d/%Y")
            newDate = datetimeObj.strftime("%Y-%m-%d")
            try:
                if override == True:
                    raise KeyError
                userLog[newDate] = current_data[newDate]
                #TODO: Finish
            except KeyError:
                dayData = self.getDataFromDay(date, runner, rid)
                userLog[newDate] = dayData
            # TODO: Add overwrite Option
        return userLog

    def writeRunnerData(
        self,
        runner: str,
        rid: str,
        dates: List[str],
        override: bool = False
    ) -> None:
        """Writes the runner's data to a file (default in ./runnerData).

        Parameters
        ----------
        Same parameters as getRunnerData

        Returns
        -------
        None

        Raises
        -------
        None

        """
        data = self.getRunnerData(runner, rid, dates, override)
        fileData = {}  # type: Dict[str, List[Dict[str, str]]]
        try:
            with open("runnerData/{0}.pkl".format(runner), "rb+") as f:
                try:
                  fileData = pickle.load(f)
                except EOFError:
                  pass
        except FileNotFoundError:
            pass
        fileData.update(data)
        if not os.path.exists("runnerData"):
            os.makedirs("runnerData")
        with open("runnerData/{0}.pkl".format(runner), "wb+") as f_pkl:
            pickle.dump(fileData, f_pkl)
        try:
            with open("runnerData/runners.txt", "r+") as f:
                currRunners = f.read()
                if runner not in currRunners:
                    f.write("{0}, {1}\n".format(runner, rid))
        except FileNotFoundError:
            with open("runnerData/runners.txt", "w+") as f:
                f.write("{0}, {1}\n".format(runner, rid))

    @staticmethod
    def loadRunnerData(runner: str) -> Dict[str, LogEntry]:
        """Load a runners data (from file).

        Parameters
        ----------
        runner : str
            Name of runner.

        Returns
        -------
        Dict[str, List[Log]]
            The runner's log.

        Raises
        -------
        None

        """
        try:
            with open(f"runnerData/{runner}.pkl", "rb") as f:
                try:
                  return pickle.load(f)
                except EOFError as e:
                  return {}
        except FileNotFoundError as e:
            return {}
