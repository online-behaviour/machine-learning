#!/usr/bin/python -W all
"""
    conversations.py: perform an analysis of conersations
    usage: conversations.py file.csv
    20170516 erikt(at)xs4all.nl
"""

import naiveBayes
import sys

COMMAND = "conversations.py"
USAGE = "usage: "+COMMAND+" file.csv"
IDCOLUMN = 0     # column id of tweet id
PARENTCOLUMN = 5 # column id of parent id (retweets and replies)
CLASSCOLUMN = 9  # column id classses 
FILEHASHEADING = False # apply to training data: has no heading line

classes = {} # classes per conversation
sizes = {} # counts of conversations with the same number of messages
uniform = {} # number of uniform conversations per size
ids = {}

if len(sys.argv) < 1: sys.exit(USAGE)
inFileName = sys.argv.pop(0)
readDataResults = naiveBayes.readData(inFileName,"",PARENTCOLUMN,CLASSCOLUMN,IDCOLUMN,FILEHASHEADING)

# link all tweet ids to their index number in the lists
id2index = {}
for i in range(0,len(readDataResults["ids"])):
    id2index[readDataResults["ids"][i]] = i

# collect classes per conversation
for i in range(0,len(readDataResults["ids"])):
    if 1000*int(i/1000) == int(i): print i
    targetI = i
    while readDataResults["text"][targetI] != "None" and \
          readDataResults["text"][targetI] in id2index.keys():
        targetI = id2index[readDataResults["text"][targetI]]
    targetId = readDataResults["ids"][targetI]
    if not targetId in classes.keys(): 
        classes[targetId] = []
        ids[targetId] = []
    # collapse classes 8 and 7
    thisClass = readDataResults["classes"][i]
    if thisClass == "8": thisClass = "7"
    classes[targetId].append(thisClass)
    ids[targetId].append(readDataResults["ids"][i])

# count inconsistencies
counter = 0
for thisId in classes.keys():
    size = str(len(classes[thisId]))
    if not size in sizes.keys(): 
        sizes[size] = 0
        uniform[size] = 0
    sizes[size] += 1
    identical = True
    for i in range(1,len(classes[thisId])):
        if classes[thisId][i] != classes[thisId][0]: 
            identical = False
            if size == "2":
                counter += 1
                print "%s # %s # %d" % (str(classes[thisId]),str(ids[thisId]),counter)
             
    if identical: uniform[size] += 1
    # if size == "2": print ids[thisId]

# show results
for size in sizes.keys():
    print "%s: %d %d" % (size,sizes[size],uniform[size])

