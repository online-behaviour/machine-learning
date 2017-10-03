#!/usr/bin/python3 -W all
"""
    select-active.py: select training lines for active learning
    usage: select-active.py -d dataFile -p probFile [-c|-r|-l|-m|-e|-S] [-R] [-a] [-s simFile] [-x]
    note: command line arguments:
    -d: data file, lines correspond with those of the probabilities file
    -p: file with probabilities; line format: class1 prob1 class2 prob2 ...
    -c: select 50% of the data based on confidence; rest at random
    -m: select data by margin  between best and second best label
    -r: select data randomly
    -e: select data by entropy of all classes
    -l: select longest lengths in characters
    -S: select highest similarity
    -R: reverse selection: not the worst but the best
    -a: output all input data, first selected, then rest
    -s: similarity file; line format: one float per line, one per data file item
    -x: print score in output before each line
    -z: size of output in lines
    -h: fill this fraction of the output with random samples (default 0.5)
    -t: select by time: oldest first 
    -D: do not delete duplicate tweets (default: delete)
    -w: in random selection leave replace the selected data in the source
    20170718 erikt(at)xs4all.nl
"""

import getopt
import math
import random
import sys

COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+" -p probFile -d dataFile [-c|-r|-l|-m|-e|-S|-t] [-R] [-a] [-s simFile] [-x] [-z size] -D -w"
EXPERIMENTSEPARATOR = "#"
sampleSize = 5503
dataFile = ""
probFile = ""
reverse = False
useRandom = False
useMargin = False
useConfidence = False
useLength = False
useEntropyAll= False
useSimilarity= False
useTime = False
outputAll = False
printScore = False
randomFraction = 0.5
deleteDuplicates = True
randomWithReplacement = False
simFile = ""
data = []

try: options = getopt.getopt(sys.argv,"acd:eh:lmp:rRs:Stxwz:",[])
except: sys.exit(USAGE)
nbrOfMethods = 0
for option in options[0]:
    if option[0] == "-c": useConfidence = True
    elif option[0] == "-d": dataFile = option[1]
    elif option[0] == "-e": useEntropyAll = True; nbrOfMethods += 1
    elif option[0] == "-p": probFile = option[1]
    elif option[0] == "-r": useRandom = True; nbrOfMethods += 1
    elif option[0] == "-l": useLength = True; nbrOfMethods += 1
    elif option[0] == "-m": useMargin = True; nbrOfMethods += 1
    elif option[0] == "-t": useTime = True; nbrOfMethods += 1
    elif option[0] == "-R": reverse = True
    elif option[0] == "-a": outputAll = True
    elif option[0] == "-s": simFile = option[1]
    elif option[0] == "-S": useSimilarity = True
    elif option[0] == "-x": printScore = True
    elif option[0] == "-z": sampleSize = int(option[1])
    elif option[0] == "-h": randomFraction = float(option[1])
    elif option[0] == "-D": deleteDuplicates = False
    elif option[0] == "-w": randomWithReplacement = True
    else: sys.exit(USAGE)
if dataFile == "": sys.exit(USAGE)
if probFile == ""  and \
   (useEntropyAll or useMargin or useConfidence): sys.exit(USAGE)
if nbrOfMethods > 1: sys.exit(COMMAND+": multiple selection methods chosen!")
if randomFraction >= 0 and randomFraction <= 1: 
   halfTarget = (1.0-randomFraction)*float(sampleSize)
else:
   sysexit(COMMAND+": unexpected value for random fraction: "+str(randomFraction))

def selectTime(data,sampleSize):
    selected = []
    while len(selected) < sampleSize and len(data) > 0:
        if reverse: index = -1
        else: index = 0
        data[index]["score"] = 1.0
        selected.append(data[index])
        data.pop(index)
    if len(selected) < sampleSize:
        sys.exit(COMMAND+": selectTime(): too few data!\n")
    return({"selected":selected,"rest":data})

def selectRandom(data,sampleSize):
    selected = []
    while len(selected) < sampleSize and len(data) > 0:
        index = int(len(data)*random.random())
        data[index]["score"] = 1.0
        selected.append(data[index])
        if not randomWithReplacement: data.pop(index)
    if len(selected) < sampleSize: 
        sys.exit(COMMAND+": selectRandom(): too few data!\n")
    return({"selected":selected,"rest":data})

def getProbs(line):
    probs = {}
    nbrOfExps = 1
    # fields format: exp1-label1 exp1-conf1 ... exp1-label12 exp1-conf12 exp2-label1
    fields = line["scores"].split()
    if len(fields) <= 0: sys.exit(COMMAND+": getProbs: empty list: fields")
    if len(fields) < 3: sys.exit(COMMAND+\
        ": getProbs: unexpected number of probabilities on line: "+str(len(fields)))
    i = 0
    while i < len(fields):
        if fields[i] == EXPERIMENTSEPARATOR: nbrOfExps += 1; i += 1
        else:
            if len(fields) < i+2: sys.exit(COMMAND+": incomplete line ("+str(i)+"): "+str(fields))
            thisClass, value = fields[i], fields[i+1]
            if thisClass in probs: probs[thisClass] += float(value) # 20170924 was 1.0
            else: probs[thisClass] = float(value) # was 1.0
            i += 2
    for c in probs: probs[c] /= nbrOfExps
    return(probs)

def computeConfidence(line):
    similarity = 1.0
    if "similarity" in line: 
        try: similarity = line["similarity"]
        except: sys.exit(COMMAND+": computeConfidence: "+line["similarity"]+" is not a number\n")
    probs = getProbs(line)
    maxProb = max(probs.values())
    if not reverse: return(maxProb*similarity) 
    else: return(maxProb/similarity)

def selectConfidence(data,sampleSize):
    selected = []
    rest = []
    counter = 0
    for line in data:
        counter += 1
        line["score"] = computeConfidence(line)
        if len(selected) >= halfTarget and \
           ((not reverse and line["score"] >= selected[-1]["score"]) or \
            (reverse and line["score"] <= selected[-1]["score"])):
            rest.append(line)
        else:
            selected.append(line)
            selected.sort(key=lambda item: item["score"],reverse=reverse)
            while len(selected) > halfTarget:
                element = selected.pop(-1)
                rest.append(element)
    randomHalf = selectRandom(rest,sampleSize-halfTarget)
    selected.extend(randomHalf["selected"])
    return({"selected":selected,"rest":randomHalf["rest"]})

def computeEntropyAll(line):
    entropy = 0.0
    similarity = 1.0
    if "similarity" in line: 
        try: similarity = line["similarity"]
        except: sys.exit(COMMAND+": computeConfidence: "+line["similarity"]+" is not a number\n")
    probs = getProbs(line)
    for thisClass in probs:
        entropy += -probs[thisClass]*math.log(probs[thisClass])/math.log(2)
    if not reverse: return(entropy*similarity) 
    else: return(entropy/similarity)

def selectEntropyAll(data,sampleSize):
    selected = []
    rest = []
    for line in data:
        line["score"] = computeEntropyAll(line)
        if len(selected) >= halfTarget and \
           ((not reverse and line["score"] <= selected[-1]["score"]) or
            (reverse and line["score"] >= selected[-1]["score"])):
            rest.append(line)
        else:
            selected.append(line)
            selected.sort(key=lambda item: item["score"],reverse=not reverse)
            while len(selected) > halfTarget:
                element = selected.pop(-1)
                rest.append(element)
    randomHalf = selectRandom(rest,sampleSize-halfTarget)
    selected.extend(randomHalf["selected"])
    return({"selected":selected,"rest":randomHalf["rest"]})

def computeMargin(line):
    similarity = 1.0
    if "similarity" in line: 
        try: similarity = line["similarity"]
        except: sys.exit(COMMAND+": computeConfidence: "+line["similarity"]+" is not a number\n")
    probs = getProbs(line)
    values = sorted(probs.values(),reverse=True)
    if len(values) < 2: margin = 0.0
    else: margin = values[1]/values[0]
    if not reverse: return(margin*similarity) 
    else: return(margin/similarity)

def selectMargin(data,sampleSize):
    selected = []
    rest = []
    for line in data:
        line["score"] = computeMargin(line)
        if len(selected) >= halfTarget and \
           ((not reverse and line["score"] <= selected[-1]["score"]) or
            (reverse and line["score"] >= selected[-1]["score"])):
            rest.append(line)
        else:
            selected.append(line)
            selected.sort(key=lambda item: item["score"],reverse=not reverse)
            while len(selected) > halfTarget:
                element = selected.pop(-1)
                rest.append(element)
    randomHalf = selectRandom(rest,sampleSize-halfTarget)
    selected.extend(randomHalf["selected"])
    return({"selected":selected,"rest":randomHalf["rest"]})

def selectLength(data,sampleSize):
    selected = []
    rest = []
    for line in data:
        line["score"] = float(len(line["data"]))
        similarity = 1.0
        if "similarity" in line: 
            try: similarity = line["similarity"]
            except: sys.exit(COMMAND+": setLength: "+line["similarity"]+" is not a number\n")
        if not reverse: line["score"] *= similarity
        else: line["score"] /= similarity
        if len(selected) >= halfTarget and \
           ((not reverse and line["score"] <= selected[-1]["score"]) or \
            (reverse and line["score"] >= selected[-1]["score"])):
            rest.append(line)
        else:
            selected.append(line)
            selected.sort(key=lambda item: item["score"],reverse=not reverse)
            while len(selected) > halfTarget:
                element = selected.pop(-1)
                rest.append(element)
    randomHalf = selectRandom(rest,sampleSize-halfTarget)
    selected.extend(randomHalf["selected"])
    return({"selected":selected,"rest":randomHalf["rest"]})

def selectSimilarity(data,sampleSize):
    selected = []
    rest = []
    for line in data:
        if not "similarity" in line: line["score"] = 1.0
        else: line["score"] = line["similarity"]
        if len(selected) >= halfTarget and \
           ((not reverse and line["score"] <= selected[-1]["score"]) or \
            (reverse and line["score"] >= selected[-1]["score"])):
            rest.append(line)
        else:
            selected.append(line)
            selected.sort(key=lambda item: item["score"],reverse=not reverse)
            while len(selected) > halfTarget:
                element = selected.pop(-1)
                rest.append(element)
    randomHalf = selectRandom(rest,sampleSize-halfTarget)
    selected.extend(randomHalf["selected"])
    return({"selected":selected,"rest":randomHalf["rest"]})

### main

try: dataStream = open(dataFile,"r")
except: sys.exit(COMMAND+": cannot read file "+dataFile+"\n")
if probFile != "":
   try: probStream = open(probFile,"r")
   except: sys.exit(COMMAND+": cannot read file "+probFile+"\n")
if simFile != "":
   try: simStream = open(simFile,"r")
   except: sys.exit(COMMAND+": cannot read file "+simFile+"\n")

seen = {}
probsSeen = False
for dataLine in dataStream:
    dataLine = dataLine.rstrip()
    line = { "data":dataLine }
    if probFile != "":
        probLine = probStream.readline()
        if probLine != "": 
           probLine = probLine.rstrip()
           line["scores"] = probLine
           probsSeen = True
    if simFile != "":
        simLine = simStream.readline()
        if simLine == "": sys.exit(COMMAND+": too few lines in similarity file "+simFile)
        simLine = simLine.rstrip()
        try: line["similarity"] = float(simLine)
        except: sys.exit(COMMAND+": "+simLine+" is not a number")
    if not dataLine in seen or not deleteDuplicates:
        data.append(line)
        seen[dataLine] = True
if probFile != "": probStream.close()
dataLine = dataStream.readline()
dataStream.close()
if dataLine != "": sys.exit(COMMAND+": too many lines in data file "+dataFile)
if simFile != "":
    simLine = simStream.readline()
    simStream.close()
    if simLine != "": sys.exit(COMMAND+": too many lines in sim file "+simFile)

if useRandom: selectResults = selectRandom(data,sampleSize)
elif useTime: selectResults = selectTime(data,sampleSize)
elif useLength: selectResults = selectLength(data,sampleSize)
elif useMargin and probsSeen: selectResults = selectMargin(data,sampleSize)
elif useConfidence and probsSeen: selectResults = selectConfidence(data,sampleSize)
elif useEntropyAll and probsSeen: selectResults = selectEntropyAll(data,sampleSize)
elif useSimilarity: selectResults = selectSimilarity(data,sampleSize)
else: selectResults = selectRandom(data,sampleSize)

for line in selectResults["selected"]:
    if printScore: print("%0.3f" % (line["score"]),end=" ")
    print("%s" % (line["data"]))
if outputAll:
    for line in selectResults["rest"]:
        if printScore:
            if not "score" in line: line["score"] = 0.0
            print("%0.3f" % (line["score"]),end=" ")
        print("%s" % (line["data"]))

