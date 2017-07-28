#!/usr/bin/python3 -W all
"""
    similarity: compute the cosine similarities of a set of numeric vectors
    usage: similarity [file2] < file1
    note: files contain one numeric vector per line, numbers separated by spaces
          paper: Settles & Craven 2008, section 3.4, pages 1074-1075
    20170725 erikt(at)xs4all.nl
"""

import math
import numpy as np
import sys

COMMAND = sys.argv.pop(0)

def computeSimilarity(vector1,vector2):
    similarity = np.inner(vector1["fields"],vector2["fields"])
    similarity /= vector1["size"]*vector2["size"]
    return(similarity)

vectors1 = []
vectors2 = []
vectors2used = False
similarities1 = []
similarities2 = []
nbrOfTokens = -1
counter = 0
if len(sys.argv) > 0:
    inFileName = sys.argv.pop(0)
    try: inFileHandle = open(inFileName,"r")
    except: sys.exit(COMMAND+": cannot read file: "+inFileName+"\n")
    vectors2used = True
    for line in inFileHandle:
        line = line.rstrip()
        fields = line.split()
        fieldsNPstrings = np.array(fields)
        fieldsNP = fieldsNPstrings.astype(float)
        size = math.sqrt(np.inner(fieldsNP,fieldsNP))
        vector = {"size":size,"fields":fieldsNP}
        vectors2.append(vector)
    inFileHandle.close()
for line in sys.stdin:
    counter += 1
    if counter == 1000*int(counter/1000): 
        sys.stderr.write(str(counter)+"\n")
        sys.stderr.flush()
    line = line.rstrip()
    fields = line.split()
    if nbrOfTokens < 0: nbrOfTokens = len(fields)
    if len(fields) != nbrOfTokens: sys.exit(COMMAND+": inconsistent number of tokens per line: "+str(nbrOfTokens)+" vs "+str(len(fields)))
    fieldsNPstrings = np.array(fields)
    fieldsNP = fieldsNPstrings.astype(float)
    size = math.sqrt(np.inner(fieldsNP,fieldsNP))
    vector = {"size":size,"fields":fieldsNP}
    similarity1 = 1.0 # = computeSimilarity(vector,vector)
    for i in range(0,len(vectors1)):
        s = computeSimilarity(vector,vectors1[i])
        similarity1 += s
        similarities1[i] += s
    vectors1.append(vector)
    similarities1.append(similarity1)
    if vectors2used:
        similarity2 = 0.0
        for i in range(0,len(vectors2)):
            similarity2 += computeSimilarity(vector,vectors2[i])
        similarities2.append(similarity2)
for i in range(0,len(similarities1)): 
    if vectors2used: similarities1[i] /= similarities2[i]
    else: similarities1[i] /= len(vectors1)
    print("%0.3f" % (similarities1[i]))

