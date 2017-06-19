#!/usr/bin/python -W all
"""
    changeCsv.py: change the values in a column of a csv file
    usage: ./changeCsv < inFile > outFile
    20170619 erikt(at)xs4all.nl
"""

import csv
import sys

# constants
COMMAND=sys.argv.pop(0)
COLUMN=9
CHANGES={"6":"5","7":"6","8":"7","9":"8","10":"9","11":"10","12":"11","13":"12"}

csvreader = csv.reader(sys.stdin,delimiter=',',quotechar='"')
csvwriter = csv.writer(sys.stdout,delimiter=',',quotechar='"')
for row in csvreader:
    if len(row) < COLUMN+1: sys.exit(COMMAND+": unexpected line: "+str(row))
    if row[COLUMN] in CHANGES: row[COLUMN] = CHANGES[row[COLUMN]]
    csvwriter.writerow(row)
