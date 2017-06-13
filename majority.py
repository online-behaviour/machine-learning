#!/usr/bin/python -W all
"""
    majority.py: select the majority class of a set of classes
    usage: majority.py < file
    note: expects the same number of classes on each line, space-separated
    20170613 erikt(at)xs4all.nl
"""

import sys

COMMAND = sys.argv.pop(0)

nbrOfTokens = -1
for line in sys.stdin:
    # remove final newline
    line = line.rstrip()
    # get the tokens on the line
    tokens = line.split()
    # check the number of tokens on the line
    if nbrOfTokens < 0: nbrOfTokens = len(tokens)
    if nbrOfTokens != len(tokens):
        sys.exit(COMMAND+": unexpected number of tokens on line: "+line)
    # count the classes on this line
    classes = {}
    for thisClass in tokens:
        if thisClass in classes: classes[thisClass] += 1
        else: classes[thisClass] = 1
    # find the most frequent class
    bestClass = ""
    bestCount = 0
    for thisClass in sorted(classes):
        if classes[thisClass] > bestCount:
            bestClass = thisClass
            bestCount = classes[thisClass]
    # print the most frequent class
    print bestClass+" "+str(bestCount)

