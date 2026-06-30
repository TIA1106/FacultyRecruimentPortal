import os
import re

logbook_path = "d:/Faculty Recruitment Portal/logs/daily_logbook (2).md"
with open(logbook_path, "r", encoding="utf-8") as f:
    content = f.read()

# Define the date mappings
date_mappings = {
    r"\[Internship Start Date\]": "2026-05-25",
    r"\[Day 2 Date\]": "2026-05-26",
    r"\[Day 3 Date\]": "2026-05-27",
    r"\[Day 4 Date\]": "2026-05-28",
    r"\[Day 5 Date\]": "2026-05-29",
    r"\[Day 6 Date\]": "2026-05-30",
    r"\[Day 7 Date\]": "2026-05-31",
    r"\[Day 8 Date\]": "2026-06-01",
    r"\[Day 9 Date\]": "2026-06-02",
    r"\[Day 10 Date\]": "2026-06-03",
    r"\[Day 11 Date\]": "2026-06-04",
    r"\[Day 12 Date\]": "2026-06-05",
    r"\[Day 13 Date\]": "2026-06-06",
    r"\[Day 14 Date\]": "2026-06-07",
    r"\[Day 15 Date\]": "2026-06-08",
    r"\[Day 16 Date\]": "2026-06-09",
    r"\[Day 17 Date\]": "2026-06-10",
    r"\[Day 18 Date\]": "2026-06-11",
    r"\[Day 19 Date\]": "2026-06-12",
    r"\[Day 20 Date\]": "2026-06-13",
    r"\[Day 21 Date\]": "2026-06-14",
    r"\[Day 22 Date\]": "2026-06-15",
    r"\[Day 23 Date\]": "2026-06-16",
    r"\[Day 24 Date\]": "2026-06-17",
    r"\[Day 25 Date\]": "2026-06-18",
    r"\[Day 26 Date\]": "2026-06-19",
    r"\[Day 27 Date\]": "2026-06-20",
    r"\[Day 28 Date\]": "2026-06-21",
    r"\[Day 29 Date\]": "2026-06-22",
    r"\[Day 30 Date\]": "2026-06-23",
    r"\[Day 31 Date\]": "2026-06-24",
    r"\[Day 32 Date\]": "2026-06-25",
    r"\[Day 33 Date\]": "2026-06-26",
    r"\[Day 34 Date\]": "2026-06-27",
    r"\[Day 35 Date\]": "2026-06-28",
    r"\[Day 36 Date\]": "2026-06-29",
    r"\[Day 37 Date\]": "2026-06-30",
    r"\[Day 38 Date\]": "2026-07-01",
    r"\[Day 39 Date\]": "2026-07-02",
    r"\[Day 40 Date\]": "2026-07-03",
    r"\[Day 41 Date\]": "2026-07-04",
    r"\[Day 42 Date\]": "2026-07-05",
    r"\[Day 43 Date\]": "2026-07-06",
    r"\[Day 44 Date\]": "2026-07-07",
    r"\[Day 45 Date\]": "2026-07-09"
}

# Perform replacement
new_content = content
for pattern, date in date_mappings.items():
    new_content = re.sub(pattern, date, new_content)

# Also ensure "JK Lakshmipat University, Jaipur" is used throughout
new_content = new_content.replace("JK Lakshmipat University", "JK Lakshmipat University, Jaipur")

# Write back
with open(logbook_path, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Successfully updated dates in daily_logbook (2).md")
