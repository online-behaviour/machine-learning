#!/usr/bin/python3 -W all
"""
    select-active.py: select training lines for active learning
    usage: select-active.py -d dataFile -p probFile [-c] [-r]
    note: command line arguments:
    -d: data file, lines correspond with those of the probabilities file
    -p: file with probabilities; line format: class1 prob1 class2 prob2 ...
    -c: select 50% of the data based on confidence; rest at random
    -r: select data randomly
    -e: select data by entropy of the best choice
    20170718 erikt(at)xs4all.nl
"""

import getopt
import math
import random
import sys

COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+" -p probFile -d dataFile [-c] [-r] [-e]"
SAMPLESIZE = 1000
HALFTARGET = int(float(SAMPLESIZE)/2.0)

dataFile = ""
probFile = ""
useRandom = False
useConfidence = False
useEntropy = False
data = []

try: options = getopt.getopt(sys.argv,"cd:ep:r",[])
except: sys.exit(USAGE)
for option in options[0]:
    if option[0] == "-c": useConfidence = True
    elif option[0] == "-d": dataFile = option[1]
    elif option[0] == "-e": useEntropy = True
    elif option[0] == "-p": probFile = option[1]
    elif option[0] == "-r": useRandom = True
if probFile == "" or dataFile == "": sys.exit(USAGE)

def selectRandom(data):
    selected = []
    while len(selected) < SAMPLESIZE and len(data) > 0:
        index = int(len(data)*random.random())
        data[index]["score"] = 1.0
        selected.append(data[index])
        data[index] = data[-1]
        data.pop(-1)
    if len(selected) < SAMPLESIZE: sys.exit(COMMAND+": selectRandom(): out of data!\n")
    return(selected)

def selectConfidence(data):
    selected = []
    rest = []
    for line in data:
        fields = line["scores"].split()
        if len(fields) <= 0: sys.exit(COMMAND+": selectConfidence: missing score\n")
        line["score"] = float(fields[1])
        if len(selected) >= HALFTARGET and line["score"] >= selected[-1]["score"]:
            rest.append(line)
        else:
            selected.append(line)
            selected.sort(key=lambda item: item["score"])
            while len(selected) > HALFTARGET:
                element = selected.pop(-1)
                rest.append(element)
    while len(selected) < SAMPLESIZE and len(rest) > 0:
        index = int(len(rest)*random.random())
        fields = rest[index]["scores"].split()
        if len(fields) <= 0: sys.exit(COMMAND+": selectConfidence: missing score\n")
        rest[index]["score"] = float(fields[1])
        selected.append(rest[index])
        rest[index] = rest[-1]
        rest.pop(-1)
    if len(selected) < SAMPLESIZE: sys.exit(COMMAND+": selectConfidence(): out of data!\n")
    return(selected)

def computeEntropy(fields):
    total = 0
    entropy = 0.0
    classes = {}
    # fields format: exp1-label1 exp1-conf1 ... exp1-label12 exp1-conf12 exp2-label1
    for i in range(0,len(fields),24):
        total += 1
        if fields[i] in classes: classes[fields[i]] += 1
        else: classes[fields[i]] = 1
    for thisClass in classes:
        p = classes[thisClass]/total
        entropy += -p*math.log(p)/math.log(2)
    return(entropy) 

def selectEntropy(data):
    selected = []
    rest = []
    entropy = []
    for line in data:
        fields = line["scores"].split()
        if len(fields) <= 0: sys.exit(COMMAND+": selectConfidence: missing score\n")
        line["score"] = computeEntropy(fields)
        if len(selected) >= HALFTARGET and line["score"] <= selected[-1]["score"]:
            rest.append(line)
        else:
            # print("%0.3f %s" % (line["score"],line))
            selected.append(line)
            selected.sort(key=lambda item: item["score"],reverse=True)
            while len(selected) > HALFTARGET:
                element = selected.pop(-1)
                rest.append(element)
    while len(selected) < SAMPLESIZE and len(rest) > 0:
        index = int(len(rest)*random.random())
        fields = rest[index]["scores"].split()
        if len(fields) <= 0: sys.exit(COMMAND+": selectConfidence: missing score\n")
        rest[index]["score"] = float(fields[1])
        selected.append(rest[index])
        rest[index] = rest[-1]
        rest.pop(-1)
    if len(selected) < SAMPLESIZE: sys.exit(COMMAND+": selectConfidence(): out of data!\n")
    return(selected)

try: probStream = open(probFile,"r")
except: sys.exit(COMMAND+": cannot read file "+probFile+"\n")
try: dataStream = open(dataFile,"r")
except: sys.exit(COMMAND+": cannot read file "+dataFile+"\n")

for probLine in probStream:
    probLine = probLine.rstrip()
    dataLine = dataStream.readline()
    if dataLine == "": sys.exit(COMMAND+": too few lines in data file "+dataFile)
    dataLine = dataLine.rstrip()
    line = { "scores":probLine, "data":dataLine }
    data.append(line)
probStream.close()
dataLine = dataStream.readline()
dataStream.close()
if dataLine != "": sys.exit(COMMAND+": too many lines in data file "+dataFile)

if useRandom: selectResults = selectRandom(data)
elif useConfidence: selectResults = selectConfidence(data)
elif useEntropy: selectResults = selectEntropy(data)
else: selectResults = selectRandom(data)

for line in selectResults:
    print("%0.3f %s" % (line["score"],line["data"]))

