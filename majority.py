#!/usr/bin/python -W all
"""
    majority.py: select the majority class of a set of classes
    usage: majority.py [prob] < file
    notes: expects the same number of classes on each line, space-separated
           optional argument prob indicates presence of class probabilities
    20170613 erikt(at)xs4all.nl
"""

import operator
import re
import sys

COMMAND = sys.argv.pop(0)
NBROFEXPERIMENTS = 25

expectProbabilities = False
bestNtoShow = 1
if len(sys.argv) > 0:
    if sys.argv[0] != "prob": 
        sys.exit(COMMAND+": unknown argument: "+sys.argv[0]+"!\n")
    else:
        expectProbabilities = True
        if len(sys.argv) > 1:
            patternNumber = re.compile("^\d+$")
            if not patternNumber.match(sys.argv[1]):
                sys.exit(COMMAND+": second argument should be number: "+sys.argv[1]+"!\n")
            else: bestNtoShow = int(sys.argv[1])
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
    if not expectProbabilities:
        for i in range(0,len(tokens)):
            if tokens[i] in classes: classes[tokens[i]] += 1
            else: classes[tokens[i]] = 1
    else:
        for i in range(0,len(tokens),2):
            if i+1 >= len(tokens): sys.exit(COMMAND+": missing probability on line: "+line+"\n")
            if tokens[i] in classes: classes[tokens[i]] += float(tokens[i+1])
            else: classes[tokens[i]] = float(tokens[i+1])
    # find the most frequent class
    counter = 0
    for i in sorted(classes.items(),key=operator.itemgetter(1),reverse=True):
        (thisClass,count) = i
        percentage = 0
        if len(tokens) > 0: 
            percentage = float(count)/float(NBROFEXPERIMENTS)
        sys.stdout.write(str(nbrOfTokens)+" "+str(bestNtoShow)+" "+str(count)+" "+str(len(tokens))+" ")
        sys.stdout.write(thisClass+" "+str(percentage))
        counter += 1
        if counter < bestNtoShow and counter < len(classes): sys.stdout.write(" ")
        else:
            sys.stdout.write("\n")
            break

