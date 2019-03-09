from difflib import SequenceMatcher
from distance import levenshtein as lvs

def get_closest_runner_name(name: str) -> str:
    runner_names = []
    with open("runnerData/runners.txt", "r+") as f:
        text = f.read()
        for id_str in text.split("\n"):
            spl = id_str.split(",")
            runner_names.append(spl[0])

    closest_name = ""
    closest_name_score = 100
    for rname in runner_names:
        parsed_rname = rname.strip().replace(" ", "").lower()
        parsed_name = name.strip().replace(" ", "").lower()

        score = lvs(parsed_rname, parsed_name)
        if score < closest_name_score:
            closest_name_score = score
            closest_name = rname
    return closest_name
