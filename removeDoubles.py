#!/usr/bin/python -W all
"""
removeDoubles.py: remove duplicates from csv data
usage: removeDoubles.py < file
20170616 erikt(at)xs4all.nl
"""

import csv
import sys

# definition constants
COMMAND = sys.argv.pop(0)
# global variables
seen = {}

csvreader = csv.reader(sys.stdin,delimiter=',',quotechar='"')
csvwriter = csv.writer(sys.stdout,delimiter=',',quotechar='"')
for row in csvreader:
    if len(row) > 0 and row[0] != "" and not row[0] in seen: csvwriter.writerow(row)
    seen[row[0]] = True

