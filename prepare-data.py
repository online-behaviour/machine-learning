#!/usr/bin/python3 -W all
# prepare-data.py: prepare data of file 2012-nl.csv for experiments
# usage: prepare-data.py < 2012-nl.csv
# notes: 
# 1. collapses labels 5 and 6 to 5
# 2. moves labels 7-13 to 6-12
# 3. removes duplicate tweets
# 20170929 erikt(at)xs4all.nl

import csv
import sys

ID = 0
LABEL = 9

def convertLabel(label):
    if (label <= 5): return(label)
    else: return(label-1)

seen = {}
csvreader = csv.reader(sys.stdin,delimiter=',',quotechar='"')
csvwriter = csv.writer(sys.stdout,delimiter=',',quotechar='"')
for row in csvreader:
    try: row[LABEL] = str(convertLabel(int(row[LABEL])))
    except: sys.exit(COMMAND+": "+row[LABEL]+" is not a number\n")
    if not row[ID] in seen: csvwriter.writerow(row)
    seen[row[ID]] = True
