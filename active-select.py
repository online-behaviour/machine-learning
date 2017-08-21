#!/usr/bin/python3 -W all
"""
    select-active.py: select training lines for active learning
    usage: select-active.py -d dataFile -p probFile [-c|-r|-l|-m|-E|-S] [-R] [-a] [-s simFile] [-x]
    note: command line arguments:
    -d: data file, lines correspond with those of the probabilities file
    -p: file with probabilities; line format: class1 prob1 class2 prob2 ...
    -c: select 50% of the data based on confidence; rest at random
    -m: select data by margin  between best and second best label
    -r: select data randomly
    -E: select data by entropy of all classes
    -l: select longest lengths in characters
    -S: select highest similarity
    -R: reverse selection: not the worst but the best
    -a: output all input data, first selected, then rest
    -s: similarity file; line format: one float per line, one per data file item
    -x: print score in output before each line
    -z: size of output in lines
    -h: do not fill up half of the output with random samples
    20170718 erikt(at)xs4all.nl
"""

import getopt
import math
import random
import sys

COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+" -p probFile -d dataFile [-c|-r|-l|-m|-E|-S] [-R] [-a] [-s simFile] [-x] [-z size]"
NBROFEXPFIELDS = 24
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
outputAll = False
printScore = False
randomHalfSample = True
simFile = ""
data = []

try: options = getopt.getopt(sys.argv,"acd:eEhlmp:rRs:Sxz:",[])
except: sys.exit(USAGE)
nbrOfMethods = 0
for option in options[0]:
    if option[0] == "-c": useConfidence = True
    elif option[0] == "-d": dataFile = option[1]
    elif option[0] == "-E": useEntropyAll = True; nbrOfMethods += 1
    elif option[0] == "-p": probFile = option[1]
    elif option[0] == "-r": useRandom = True; nbrOfMethods += 1
    elif option[0] == "-l": useLength = True; nbrOfMethods += 1
    elif option[0] == "-m": useMargin = True; nbrOfMethods += 1
    elif option[0] == "-R": reverse = True
    elif option[0] == "-a": outputAll = True
    elif option[0] == "-s": simFile = option[1]
    elif option[0] == "-S": useSimilarity = True
    elif option[0] == "-x": printScore = True
    elif option[0] == "-z": sampleSize = int(option[1])
    elif option[0] == "-h": randomHalfSample = False
    else: sys.exit(USAGE)
if dataFile == "": sys.exit(USAGE)
if probFile == ""  and \
   (useEntropyAll or useMargin or useConfidence): sys.exit(USAGE)
if nbrOfMethods > 1: sys.exit(COMMAND+": multiple selection methods chosen!")
if randomHalfSample: halfTarget = int(float(sampleSize)/2.0)
else: halfTarget = sampleSize

def selectRandom(data,sampleSize):
    selected = []
    while len(selected) < sampleSize and len(data) > 0:
        index = int(len(data)*random.random())
        data[index]["score"] = 1.0
        selected.append(data[index])
        data.pop(index)
    if len(selected) < sampleSize: 
        sys.exit(COMMAND+": selectRandom(): too few data!\n")
    return({"selected":selected,"rest":data})

def getProbs(line):
    probs = {}
    # fields format: exp1-label1 exp1-conf1 ... exp1-label12 exp1-conf12 exp2-label1
    fields = line["scores"].split()
    if len(fields) <= 0: sys.exit(COMMAND+": getProbs: empty list: fields")
    for i in range(0,len(fields),2):
        if len(fields) < i+2: sys.exit(COMMAND+": incomplete line: "+str(fields))
        thisClass, value = fields[i], fields[i+1]
        if thisClass in probs: probs[thisClass] += float(value)
        else: probs[thisClass] = float(value)
    for c in probs: probs[c] /= len(fields)/NBROFEXPFIELDS
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
for dataLine in dataStream:
    dataLine = dataLine.rstrip()
    line = { "data":dataLine }
    if probFile != "":
        probLine = probStream.readline()
        if probLine == "": sys.exit(COMMAND+": too few lines in prob file "+probFile)
        probLine = probLine.rstrip()
        line["scores"] = probLine
    if simFile != "":
        simLine = simStream.readline()
        if simLine == "": sys.exit(COMMAND+": too few lines in similarity file "+simFile)
        simLine = simLine.rstrip()
        try: line["similarity"] = float(simLine)
        except: sys.exit(COMMAND+": "+simLine+" is not a number")
    if not dataLine in seen:
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
elif useConfidence: selectResults = selectConfidence(data,sampleSize)
elif useEntropyAll: selectResults = selectEntropyAll(data,sampleSize)
elif useLength: selectResults = selectLength(data,sampleSize)
elif useMargin: selectResults = selectMargin(data,sampleSize)
elif useSimilarity: selectResults = selectSimilarity(data,sampleSize)
else: selectResults = selectRandom(data,sampleSize)

for line in selectResults["selected"]:
    if printScore: print("%0.3f" % (line["score"]),end=" ")
    print("%s" % (line["data"]))
if outputAll:
    for line in selectResults["rest"]:
        if printScore: print("%0.3f" % (line["score"]),end=" ")
        print("%s" % (line["data"]))

