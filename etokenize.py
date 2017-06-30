#!/usr/bin/python -W all
"""
   etokenize.py: tokenize a text
   usage: etokenize [-c] < file
   notes: cannot be named tokenized.py: causes an import loop
          option -c: keep upper case characters
   20170626 erikt(at)xs4all.nl
"""

import csv
import getopt
import naiveBayes
import re
import sys

COMMAND = naiveBayes.COMMAND
USAGE = "usage: "+COMMAND+" [-c] < file"
NONE = -1
LABELPREFIX = "__label__" # label prefix of fasttext
classColumn = NONE
tweetColumn = NONE
keepUpperCase = False

try: options,arguments = getopt.getopt(sys.argv,"c",[])
except: sys.exit(USAGE)
for option in options:
    if option[0] == "-c": keepUpperCase = True

csvreader = csv.reader(sys.stdin,delimiter=',',quotechar='"')
lineNbr = 0
for row in csvreader:
    lineNbr += 1
    # first line is a heading
    if lineNbr == 1:
        for i in range(0,len(row)):
            if row[i] == "tweet": tweetColumn = i
            elif row[i] == "class" or row[i] == naiveBayes.CLASSCOLUMNNAME: classColumn = i
    else:
        # sanity check
        if tweetColumn == NONE: sys.exit(COMMAND+": tweet column definition missing in heading: "+str(row))
        # tokenize tweet text
        tokenized, = naiveBayes.tokenize([row[tweetColumn]],keepUpperCase)
        # print tokenized text
        if classColumn != NONE: sys.stdout.write(LABELPREFIX+row[classColumn]+" ")
        for i in range(0,len(tokenized)): 
            if i > 0: sys.stdout.write(" ")
            sys.stdout.write(tokenized[i].encode("utf8"))
        print
sys.exit()
