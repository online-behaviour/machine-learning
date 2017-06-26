#!/usr/bin/python -W all
"""
    selectData.py: select data for active learning
    usage: selectData.py size < file
    note: apply to the classfication of the development data (EXPERIMENTS/dev)
    20170622 erikt(at)xs4all.nl
"""

import csv
import random
import sys

COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+" size < file"
SMALLNUMBER = 0.0001
NBROFFIELDS  = 5
if len(sys.argv) <= 0: sys.exit(USAGE)
try: size = int(sys.argv.pop(0))
except: sys.exit(USAGE)

def computeFactor(row):
    try: factor =(SMALLNUMBER+float(row[2]))/(SMALLNUMBER+float(row[4]))
    except: sys.exit(COMMAND+": problem with scores in "+str(row)+"\n")
    return(factor)

# read the tweets with confidence scores: 7,7,0.930,6,0.262,...
csvreader = csv.reader(sys.stdin,delimiter=',',quotechar='"')
nbrOfFields = -1
rows = []
factors = [] # quotient of two largest confidence scores
for row in csvreader:
    if nbrOfFields < 0: nbrOfFields = len(row)
    if len(row) != nbrOfFields: sys.exit(COMMAND+": unexpected row length: "+str(row)+"\n")
    rows.append(row)
    factor = computeFactor(row)
    factors.append(factor)

# sort factors
factors.sort()
top10 = int(0.10*float(len(factors)))

# select tweets
csvwriter = csv.writer(sys.stdout,delimiter=',',quotechar='"')
for i in range(0,size,2):
    # select a difficult tweet
    r = int(float(len(rows))*random.random())
    factor = computeFactor(rows[r])
    while factor > factors[top10]:
       r = int(float(len(rows))*random.random())
       factor = computeFactor(rows[r])
    # now we have a random difficult tweet
    csvwriter.writerow(rows[r])
    # delete the tweet (draw without replacement)
    rows[r] = list(rows[-1])
    rows.pop(-1)
        # select a difficult tweet
    r = int(float(len(rows))*random.random())
    # now we have a random tweet
    csvwriter.writerow(rows[r])
    # delete the tweet (draw without replacement)
    rows[r] = list(rows[-1])
    rows.pop(-1)

