#!/usr/bin/python3 -W all
"""
    select-active.py: select training lines for active learning
    usage: select-active.py -d dataFile -p probFile [-c|-r|-e|-l|-m|-E] [-R] [-a]
    note: command line arguments:
    -d: data file, lines correspond with those of the probabilities file
    -p: file with probabilities; line format: class1 prob1 class2 prob2 ...
    -c: select 50% of the data based on confidence; rest at random
    -m: select data by margin  between best and second best label
    -r: select data randomly
    -e: select data by entropy of the best choice
    -E: select data by entropy of all classes
    -l: select longest lengths in characters
    -R: reverse selection: not the worst but the best
    -a: output all input data, first selected, then rest
    20170718 erikt(at)xs4all.nl
"""

import getopt
import math
import random
import sys

COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+" -p probFile -d dataFile [-c|-r|-e|-l|-m|-E] [-R] [-a]"
SAMPLESIZE = 2
HALFTARGET = int(float(SAMPLESIZE)/2.0)
NBROFEXPFIELDS = 24
dataFile = ""
probFile = ""
reverse = False
useRandom = False
useMargin = False
useConfidence = False
useLength = False
useEntropyBest = False
useEntropyAll= False
outputAll = False
data = []

try: options = getopt.getopt(sys.argv,"acd:eElmp:rR",[])
except: sys.exit(USAGE)
for option in options[0]:
    if option[0] == "-c": useConfidence = True
    elif option[0] == "-d": dataFile = option[1]
    elif option[0] == "-e": useEntropyBest = True
    elif option[0] == "-E": useEntropyAll = True
    elif option[0] == "-p": probFile = option[1]
    elif option[0] == "-r": useRandom = True
    elif option[0] == "-l": useLength = True
    elif option[0] == "-m": useMargin = True
    elif option[0] == "-R": reverse = True
    elif option[0] == "-a": outputAll = True
    else: sys.exit(USAGE)
if probFile == "" or dataFile == "": sys.exit(USAGE)

def selectRandom(data):
    selected = []
    duplicates = []
    seen = {}
    while len(selected) < SAMPLESIZE and len(data) > 0:
        index = int(len(data)*random.random())
        data[index]["score"] = 1.0
        if not data[index]["data"] in seen:
            selected.append(data[index])
            seen[data[index]["data"]] = True
        else: duplicates.append(data[index])
        data[index] = data[-1]
        data.pop(-1)
    if len(selected) < SAMPLESIZE: sys.exit(COMMAND+": selectRandom(): out of data!\n")
    return({"selected":selected,"rest":data+duplicates})

def computeConfidence(fields):
    probs = {}
    if len(fields) <= 0: sys.exit(COMMAND+": computeConfidence: empty list: fields")
    # fields format: exp1-label1 exp1-conf1 ... exp1-label12 exp1-conf12 exp2-label1
    for i in range(0,len(fields),2):
        if len(fields) < i+2: sys.exit(COMMAND+": incomplete line: "+str(fields))
        if fields[i] in probs: probs[fields[i]] += float(fields[i+1])
        else: probs[fields[i]] = float(fields[i+1])
    maxProb = probs[fields[0]]
    maxClass = fields[0]
    for thisClass in probs:
        if probs[thisClass] > maxProb:
            maxProb = probs[thisClass]
            maxClass = thisClass
    maxProb /= len(fields)/NBROFEXPFIELDS
    return(maxProb,maxClass)

def selectConfidence(data):
    selected = []
    rest = []
    duplicates = []
    seen = {}
    for line in data:
        fields = line["scores"].split()
        if len(fields) <= 0: sys.exit(COMMAND+": selectConfidence: missing score\n")
        line["score"],line["class"] = computeConfidence(fields)
        if len(selected) >= HALFTARGET and \
           ((not reverse and line["score"] >= selected[-1]["score"]) or \
            (reverse and line["score"] <= selected[-1]["score"])):
            rest.append(line)
        elif not line["data"] in seen:
            selected.append(line)
            seen[line["data"]] = True
            selected.sort(key=lambda item: item["score"],reverse=reverse)
            while len(selected) > HALFTARGET:
                element = selected.pop(-1)
                rest.append(element)
    while len(selected) < SAMPLESIZE and len(rest) > 0:
        index = int(len(rest)*random.random())
        if not rest[index]["data"] in seen:
            selected.append(rest[index])
            seen[rest[index]["data"]] = True
        else: duplicates.append(rest[index])
        rest[index] = rest[-1]
        rest.pop(-1)
    if len(selected) < SAMPLESIZE: sys.exit(COMMAND+": selectConfidence(): out of data!\n")
    return({"selected":selected,"rest":rest+duplicates})

def computeEntropyBest(fields):
    total = 0
    entropy = 0.0
    classes = {}
    # fields format: exp1-label1 exp1-conf1 ... exp1-label12 exp1-conf12 exp2-label1
    for i in range(0,len(fields),NBROFEXPFIELDS):
        total += 1
        if i+1 >= len(fields): 
            sys.exit(COMMAND+": computeEntropyBest: too few elements in fields: "+str(fields))
        if fields[i] in classes: classes[fields[i]] += 1
        else: classes[fields[i]] = 1
    for thisClass in classes:
        p = classes[thisClass]/total
        entropy += -p*math.log(p)/math.log(2)
    return(entropy) 

def selectEntropyBest(data):
    selected = []
    rest = []
    duplicates = []
    seen = {}
    for line in data:
        fields = line["scores"].split()
        if len(fields) <= 0: sys.exit(COMMAND+": selectEntropyBest: missing score\n")
        line["score"] = computeEntropyBest(fields)
        if len(selected) >= HALFTARGET and \
           ((not reverse and line["score"] <= selected[-1]["score"]) or
            (reverse and line["score"] >= selected[-1]["score"])):
            rest.append(line)
        elif not line["data"] in seen:
            selected.append(line)
            seen[line["data"]] = True
            selected.sort(key=lambda item: item["score"],reverse=not reverse)
            while len(selected) > HALFTARGET:
                element = selected.pop(-1)
                rest.append(element)
    while len(selected) < SAMPLESIZE and len(rest) > 0:
        index = int(len(rest)*random.random())
        if not rest[index]["data"] in seen:
            selected.append(rest[index])
            seen[rest[index]["data"]] = True
        else: duplicates.append(rest[index])
        rest[index] = rest[-1]
        rest.pop(-1)
    if len(selected) < SAMPLESIZE: sys.exit(COMMAND+": selectEntropyBest(): out of data!\n")
    return({"selected":selected,"rest":rest+duplicates})

def computeEntropyAll(fields):
    total = 0
    entropy = 0.0
    classes = {}
    # fields format: exp1-label1 exp1-conf1 ... exp1-label12 exp1-conf12 exp2-label1
    for i in range(0,len(fields),2):
        total += 1
        if i+1 >= len(fields): 
            sys.exit(COMMAND+": computeEntropyAll: too few elements in fields: "+str(fields))
        if fields[i] in classes: classes[fields[i]] += float(fields[i+1])
        else: classes[fields[i]] = float(fields[i+1])
    for thisClass in classes:
        p = classes[thisClass]/(total/NBROFEXPFIELDS)
        entropy += -p*math.log(p)/math.log(2)
    return(entropy) 

def selectEntropyAll(data):
    selected = []
    rest = []
    duplicates = []
    seen = {}
    for line in data:
        fields = line["scores"].split()
        if len(fields) <= 0: sys.exit(COMMAND+": selectEntropyAll: missing score\n")
        line["score"] = computeEntropyAll(fields)
        if len(selected) >= HALFTARGET and \
           ((not reverse and line["score"] <= selected[-1]["score"]) or
            (reverse and line["score"] >= selected[-1]["score"])):
            rest.append(line)
        elif not line["data"] in seen:
            selected.append(line)
            seen[line["data"]] = True
            selected.sort(key=lambda item: item["score"],reverse=not reverse)
            while len(selected) > HALFTARGET:
                element = selected.pop(-1)
                rest.append(element)
    while len(selected) < SAMPLESIZE and len(rest) > 0:
        index = int(len(rest)*random.random())
        if not rest[index]["data"] in seen:
            selected.append(rest[index])
            seen[rest[index]["data"]] = True
        else: duplicates.append(rest[index])
        rest[index] = rest[-1]
        rest.pop(-1)
    if len(selected) < SAMPLESIZE: sys.exit(COMMAND+": selectEntropyAll(): out of data!\n")
    return({"selected":selected,"rest":rest+duplicates})

def computeMargin(fields):
    classes = {}
    # fields format: exp1-label1 exp1-conf1 ... exp1-label12 exp1-conf12 exp2-label1
    for i in range(0,len(fields),2):
        if i+1 >= len(fields): sys.exit(COMMAND+": computeMargin: too few elements in fields: "+str(fields))
        if fields[i] in classes: classes[fields[i]] += float(fields[i+1])
        else: 
            classes[fields[i]] = float(fields[i+1])
    classValues = []
    for c in classes: classValues.append(classes[c])
    classValues.sort()
    if len(classValues) < 2: margin = 0.0
    else: margin = classValues[-2]/classValues[-1]
    return(margin) 

def selectMargin(data):
    selected = []
    rest = []
    duplicates = []
    seen = {}
    for line in data:
        fields = line["scores"].split()
        if len(fields) <= 0: sys.exit(COMMAND+": selectMargin: missing score\n")
        line["score"] = computeMargin(fields)
        if len(selected) >= HALFTARGET and \
           ((not reverse and line["score"] <= selected[-1]["score"]) or
            (reverse and line["score"] >= selected[-1]["score"])):
            rest.append(line)
        elif not line["data"] in seen:
            selected.append(line)
            seen[line["data"]] = True
            selected.sort(key=lambda item: item["score"],reverse=not reverse)
            while len(selected) > HALFTARGET:
                element = selected.pop(-1)
                rest.append(element)
    while len(selected) < SAMPLESIZE and len(rest) > 0:
        index = int(len(rest)*random.random())
        if not rest[index]["data"] in seen:
            selected.append(rest[index])
            seen[rest[index]["data"]] = True
        else: duplicates.append(rest[index])
        rest[index] = rest[-1]
        rest.pop(-1)
    if len(selected) < SAMPLESIZE: sys.exit(COMMAND+": selectMargin(): out of data!\n")
    return({"selected":selected,"rest":rest+duplicates})

def selectLength(data):
    selected = []
    rest = []
    duplicates = []
    seen = {}
    for line in data:
        line["score"] = float(len(line["data"]))
        if len(selected) >= HALFTARGET and \
           ((not reverse and line["score"] <= selected[-1]["score"]) or \
            (reverse and line["score"] >= selected[-1]["score"])):
            rest.append(line)
        elif not line["data"] in seen:
            selected.append(line)
            seen[line["data"]] = True
            selected.sort(key=lambda item: item["score"],reverse=not reverse)
            while len(selected) > HALFTARGET:
                element = selected.pop(-1)
                rest.append(element)
    while len(selected) < SAMPLESIZE and len(rest) > 0:
        index = int(len(rest)*random.random())
        if not rest[index]["data"] in seen:
            selected.append(rest[index])
            seen[rest[index]["data"]] = True
        else: duplicates.append(rest[index])
        rest[index] = rest[-1]
        rest.pop(-1)
    if len(selected) < SAMPLESIZE: sys.exit(COMMAND+": selectConfidence(): out of data!\n")
    return({"selected":selected,"rest":rest+duplicates})

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
elif useEntropyBest: selectResults = selectEntropyBest(data)
elif useEntropyAll: selectResults = selectEntropyAll(data)
elif useLength: selectResults = selectLength(data)
elif useMargin: selectResults = selectMargin(data)
else: selectResults = selectRandom(data)

for line in selectResults["selected"]:
    print("%0.3f %s" % (line["score"],line["data"]))
if outputAll:
    for line in selectResults["rest"]:
        print("%0.3f %s" % (line["score"],line["data"]))
