#!/usr/bin/python -W all
"""
    majority.py: select the majority class of a set of classes
    usage: majority.py [-p] [-i number] [-o number] < file
    notes: expects the same number of classes on each line, space-separated
           optional argument -p indicates a probabilities follows each input class
           optional argument -i indicates the number of input classes per experiment (default 1)
           optional argument -o specifies the number of best classes to output (default 1)
    20170613 erikt(at)xs4all.nl
"""

import getopt
import operator
import re
import sys

COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+" [-p] [-i number] [-o number]"

expectProbabilities = False
nbrOfInputPerExperiment = 1
bestNtoShow = 1

try: options = getopt.getopt(sys.argv,"pi:o:",[])
except: sys.exit(USAGE)
for option in options[0]:
    if option[0] == "-p": expectProbabilities = True
    elif option[0] == "-i": 
       try: nbrOfInputPerExperiment = int(option[1])
       except: sys.exit(USAGE)
    elif option[0] == "-o": 
       try: bestNtoShow = int(option[1])
       except: sys.exit(USAGE)

nbrOfTokens = -1

for line in sys.stdin:
    line = line.rstrip()
    tokens = line.split()
    if nbrOfTokens < 0: nbrOfTokens = len(tokens)
    if nbrOfTokens != len(tokens):
        sys.exit(COMMAND+": unexpected number of tokens on line: "+line)
    # compute the total of frequency score per class
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
    #  the most frequent classes
    counter = 0
    for i in sorted(classes.items(),key=operator.itemgetter(1),reverse=True):
        (thisClass,count) = i
        percentage = 0
        if len(tokens) > 0: 
            percentage = float(nbrOfInputPerExperiment)*float(count)/float(len(tokens))
        if expectProbabilities:
            percentage *= 2.0
        sys.stdout.write(thisClass+" "+str(percentage))
        counter += 1
        if counter < bestNtoShow and counter < len(classes): sys.stdout.write(" ")
        else:
            sys.stdout.write("\n")
            break

