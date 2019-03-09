from typing import List

class LogItem():
    def __init__(
        self,
        date: str,
        workout_type: str,
        title: str,
        tod: str,
        route: str,
        distance_str: str,
        time: str,
        shoes: str,
        warmup_cooldown_str: str,
        temperature: str,
        conditions: str,
        wind: str,
        sleep: str
    ):
        self.date = date
        self.type = workout_type
        self.tod = tod
        self.time = time
        self.route = route
        self.shoes = shoes
        self.distance = self.convert_to_miles(distance_str) if distance_str != "" else 0
        self.warmup_cooldown = self.convert_to_miles(warmup_cooldown_str) if warmup_cooldown_str != "" else 0
        self.temperature = temperature
        self.conditions = conditions
        self.wind = wind
        self.sleep = sleep


    def convert_to_miles(self, distance_str: str) -> float:
        if "miles" in distance_str:
            return self.distance_miles(distance_str)
        elif "kilometers" in distance_str:
            return self.distance_km(distance_str)
        elif "meters" in distance_str:
            return self.distance_meters(distance_str)
        elif "yards" in distance_str:
            return self.distance_yards(distance_str)
        elif distance_str.find(" ") == -1:
            return float(distance_str)
        else:
            raise ValueError("distance_str not of miles, kilometers, meters or yards.")

    def distance_miles(self, distance_str: str) -> float:
        return float(distance_str.replace(" miles", ""))

    def distance_km(self, distance_str: str) -> float:
        kms = float(distance_str.replace(" kilometers", ""))
        return kms * 0.62137119 # 1km = 0.62137119 mile

    def distance_meters(self, distance_str: str) -> float:
        kms = float(distance_str.replace(" meters", ""))/1000
        return kms * 0.62137119 # 1km = 0.62137119 mile

    def distance_yards(self, distance_str: str) -> float:
        yards = float(distance_str.replace(" yards", ""))
        return yards / 1760

class LogEntry():
    def __init__(self, items: List[LogItem]):
        self.items = items

    def add_log(self, item: LogItem) -> None:
        self.items.append(item)
