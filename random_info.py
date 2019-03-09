import GenJSON
import re

runners = GenJSON.getRunners()
names = runners.keys()

for name in names:
    two_names_re_obj = re.fullmatch("[A-Z][^ ]* [A-Z][^ ]*", name)
    three_names_re_obj = re.fullmatch("[A-Z][^ ]* [A-Z][^ ]* [A-Z][^ ]*", name)
    if two_names_re_obj is None and three_names_re_obj is None:
        print(name)