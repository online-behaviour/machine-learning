#!/usr/bin/python3 -W all
"""
    nearest-neighbors.py: compute the nearest neighbors of numeric vectors
    usage: nearest-neighbors.py < file1
    notes: files contain one numeric vector per line, numbers separated by spaces
          based on similarity.py
    20170822 erikt(at)xs4all.nl
"""

import math
import numpy as np
import sys

COMMAND = sys.argv.pop(0)

def computeSimilarity(vector1,vector2):
    similarity = np.inner(vector1["fields"],vector2["fields"])
    similarity /= vector1["size"]*vector2["size"]
    return(similarity)

vectors = []
bestSimilarities = []
nbrOfTokens = -1
counter = 0
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
    bestSimilarity = 0.0
    bestNeighbor = -1
    for i in range(0,len(vectors)):
        s = computeSimilarity(vector,vectors[i])
        if s > bestSimilarity: 
           bestSimilarity = s
           bestNeighbor = i
        if s > bestSimilarities[i]["similarity"]: 
           bestSimilarities[i]["similarity"] = s
           bestSimilarities[i]["neighbor"] = len(bestSimilarities)
    vectors.append(vector)
    bestSimilarities.append({"similarity":bestSimilarity,"neighbor":bestNeighbor})
for i in range(0,len(bestSimilarities)): 
    print("%0.3f %d" % (bestSimilarities[i]["similarity"],bestSimilarities[i]["neighbor"]))

