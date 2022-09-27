import sys

import os

os.open("home/max/Download/", 2)


try:
    f = open(".navr", "r")
except FileNotFoundError as err:
    print(str(err) + ": Populate with `nav add`")
    sys.exit(1)

lines = f.readlines()

print(lines)

# user_input = input()
user_input = "Dow"

# search = "Down" in lines
search = filter(lambda l: user_input.lower() in l.lower(), lines)

# return string with no new lines
o = list(search)[0]
o = o.replace("\n", "")

print(o)
