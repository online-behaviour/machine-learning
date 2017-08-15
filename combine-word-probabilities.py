#!/usr/bin/python3 -W all
"""
combine-word-probabilities.py: combine label probabilities of words in tweet
usage: combine-word-probabilities.py -p prob-file -t test-file
notes: prob-file: line format: word label1 prob1 label2 prob2 ...
       test-file: label tweet
20170815 erikt(at)xs4all.nl
"""

import getopt
import sys

COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+" -p prob-file -t test-file"
NBROFLABELS = 12

probFileName = ""
testFileName = ""

try: options = getopt.getopt(sys.argv,"p:t:",[])
except: sys.exit(USAGE)
for option in options[0]:
    if option[0] == "-p": probFileName = option[1]
    elif option[0] == "-t": testFileName = option[1]
if probFileName == "" or testFileName == "": sys.exit(USAGE)

# read probabilities
mydict = {}
allProbs = {}
nbrOfTokens = 0;
try: probFileHandle = open(probFileName,"r")
except: sys.exit(COMMAND+": cannot read file "+probFileName+"!\n")
for line in probFileHandle:
    line = line.rstrip()
    tokens = line.split()
    word = tokens.pop(0)
    nbrOfTokens += 1
    probs = {}
    for i in range(0,len(tokens),2):
        if i+1 >= len(tokens): sys.exit(COMMAND+": incomplete line: "+line+"\n")
        probs[tokens[i]] = float(tokens[i+1])
        if tokens[i] in allProbs: allProbs[tokens[i]] += float(tokens[i+1])
        else: allProbs[tokens[i]] = float(tokens[i+1])
    mydict[word] = probs.copy()
probFileHandle.close()
for token in mydict:
    for label in mydict[token]:
        mydict[token][label] /= allProbs[label]/nbrOfTokens

# process tweets
try: testFileHandle = open(testFileName,"r")
except: sys.exit(COMMAND+": cannot read file "+testFileName+"!\n")
for line in testFileHandle:
    line = line.rstrip()
    tokens = line.split()
    probs = {}
    for i in range(0,len(tokens)):
        if tokens[i] in mydict:
            for label in sorted(mydict[tokens[i]],key=mydict[tokens[i]].get,reverse=True):
                if label in probs: probs[label] += mydict[tokens[i]][label]
                else: probs[label] = mydict[tokens[i]][label]
    for label in sorted(probs,key=probs.get,reverse=True): 
        sys.stdout.write(label+" "+str(probs[label])+" ")
    sys.stdout.write("\n")
testFileHandle.close()

