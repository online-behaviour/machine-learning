#!/usr/bin/python3 -W all
"""
    select-active.py: select training lines for active learning
    usage: select-active.py -d dataFile -p probFile
    note: command line arguments:
    -d: data file, lines correspond with those of the probabilities file
    -p: file with probabilities; line format: class1 prob1 class2 prob2 ...
    20170718 erikt(at)xs4all.nl
"""

import getopt
import random
import sys

COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+" -p probFile -d dataFile"
SAMPLESIZE = 1000
BESTSAMPLETARGET = int(float(SAMPLESIZE)/2.0)

dataFile = ""
probFile = ""
bestSample = []
otherData = []

try: options = getopt.getopt(sys.argv,"d:p:",[])
except: sys.exit(USAGE)
for option in options[0]:
    if option[0] == "-d": dataFile = option[1]
    elif option[0] == "-p": probFile = option[1]
if probFile == "" or dataFile == "": sys.exit(USAGE)

try: probStream = open(probFile,"r")
except: sys.exit(COMMAND+": cannot read file "+probFile+"\n")
try: dataStream = open(dataFile,"r")
except: sys.exit(COMMAND+": cannot read file "+dataFile+"\n")

for probLine in probStream:
    probLine = probLine.rstrip()
    fields = probLine.split()
    score = float(fields[1])
    try: dataLine = dataStream.readline()
    except: sys.exit(COMMAND+": too few lines in data file "+dataFile+"\n")
    dataLine = dataLine.rstrip()
    line = { "score":score, "data":dataLine }
    if len(bestSample) >= BESTSAMPLETARGET and line["score"] >= bestSample[-1]["score"]:
        otherData.append(line)
    else:
        bestSample.append(line)
        bestSample.sort(key=lambda item: item["score"])
        while len(bestSample) > BESTSAMPLETARGET:
            element = bestSample.pop(-1)
            otherData.append(element)
probStream.close()
try: 
    dataLine = dataStram.readline()
    dataStreamc.lose()
    sys.exit(COMMAND+": too many lines in data file "+dataFile+"\n")
except:
    dataStream.close()

for line in bestSample:
    print("%0.3f %s" % (line["score"],line["data"]))
for i in range(0,SAMPLESIZE-BESTSAMPLETARGET):
    if len(otherData) <= 0: sys.exit(COMMAND+": error: out of data")
    index = int(len(otherData)*random.random())
    print("%0.3f %s" % (otherData[index]["score"],otherData[index]["data"]))
    otherData[index] = otherData[-1]
    otherData.pop(-1)

