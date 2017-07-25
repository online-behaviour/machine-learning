#!/usr/bin/python3 -W all
"""
    similarity: compute the cosine similarities of a set of numeric vectors
    usage: similarity < file
    note: file contains one numeric vector per line, numbers separated by spaces
    20170725 erikt(at)xs4all.nl
"""

import math
import sys

COMMAND = sys.argv.pop(0)

def computeSimilarity(vector1,vector2):
    similarity = 0.0
    for i in range(0,len(vector1["vector"])):
        similarity += vector1["vector"][i]*vector2["vector"][i]
    similarity /= vector1["length"]*vector2["length"]
    return(similarity)

def computeLength(data):
    length = 0.0
    for i in range(0,len(data)): length += data[i]*data[i]
    length = math.sqrt(length)
    return(length)

vectors = []
similarities = []
nbrOfTokens = -1
counter = 0
for line in sys.stdin:
    counter += 1
    if counter == 100*int(counter/100): 
        print(str(counter))
        sys.stdout.flush()
    line = line.rstrip()
    fields = line.split()
    if nbrOfTokens < 0: nbrOfTokens = len(fields)
    if len(fields) != nbrOfTokens: sys.exit(COMMAND+": inconsistent number of tokens per line: "+str(nbrOfTokens)+" vs "+str(len(fields)))
    for i in range(0,len(fields)): fields[i] = float(fields[i])
    length = computeLength(fields)
    vector = {"length":length,"vector":fields}
    similarity = 0.0
    for i in range(0,len(vectors)):
        s = computeSimilarity(vector,vectors[i])
        similarity += s
        similarities[i] += s
    vectors.append(vector)
    similarities.append(similarity)
for i in range(0,len(similarities)): 
    print("%0.3f" % (similarities[i]/len(vectors)))

