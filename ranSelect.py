#!/usr/bin/python -W all
"""
    ranSelect.py: show data from a random line of a csv file
    usage: ranSelect.py < file.csv
    20170501 erikt(at)xs4all.nl
"""

import csv
import random
import re
import sys

TWEETCOLUMN = 4
CLASSCOLUMN = 9
HASHEADING = False

# read the data from training or test file
def readData(tweetColumn,classColumn,fileHasHeading):
    text = [] # list with tweet texts
    classes = [] # list with tweet classes
    with sys.stdin as csvfile:
        csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
        lineNbr = 0
        for row in csvreader:
            lineNbr += 1
            # ignore first line if it is a heading
            if lineNbr == 1 and fileHasHeading: continue
            # add tweet text to list
            text.append(row[tweetColumn])
            # add tweet class to list
            classes.append(row[classColumn])
        csvfile.close()
    # return results
    return({"text":text, "classes":classes})

# read the data
readDataResults = readData(TWEETCOLUMN,CLASSCOLUMN,HASHEADING)
index = int(float(len(readDataResults["text"]))*random.random())
print "%s %s" % (readDataResults["classes"][index],readDataResults["text"][index])

# done
sys.exit()
