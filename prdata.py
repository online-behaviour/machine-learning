#!/usr/bin/python -W all
# prdata: compute precision and recall data classifier output
# usage: eval < file
# notes: 
# - expects line to end with: gold tag, guessed tag and score
# - assumes that there are two tags: O and 1
# 20170413 erikt(at)xs4all.nl

import re
import sys

OTHER = "O"

correct = {} # dictionary with correct counts
gold = {}    # dictionary with gold tag counts
guessed = {} # dictionary with guessed tag counts
goldTotal = 0

for line in sys.stdin:
    # remove final newline
    line = line.rstrip()
    # get the tokens on the line
    tokens = line.split()
    # check if the line contains at least three tokens
    if len(tokens) <= 2: continue
    # get score, gold tag and guessed tag
    score = tokens.pop(-1)
    guessedTag = tokens.pop(-1)
    goldTag = tokens.pop(-1)
    # assume that there are two tags only
    if guessedTag != OTHER: guessedTag = "1"
    if goldTag != OTHER: goldTag = "1"
    # check if the guess is correct
    if guessedTag == goldTag:
        if not score in correct: correct[score] = {}
        if goldTag in correct[score]: correct[score][goldTag] += 1
        else: correct[score][goldTag] = 1
    # add the gold tag to the counts
    if not score in gold: gold[score] = {}
    if goldTag in gold[score]: gold[score][goldTag] += 1
    else: gold[score][goldTag] = 1
    # add the guessed tag to the counts
    if not score in guessed: guessed[score] = {}
    if guessedTag in guessed[score]: guessed[score][guessedTag] += 1
    else: guessed[score][guessedTag] = 1
    # increase gold counter when the gold tag is 1
    if goldTag == "1": goldTotal += 1

# show results
for threshold in sorted(gold.iterkeys(),key=float):
    # compute new guesses based on the threshold value
    newCorrect = 0
    newGuessed = 0
    for tag in gold:
        if not tag in gold: gold[tag] = {}
        if not "1" in gold[tag]: gold[tag]["1"] = 0
        if not OTHER in gold[tag]: gold[tag][OTHER] = 0
        if (float(tag) >= float(threshold)):
            # guess 1
            newGuessed += gold[tag][OTHER]+gold[tag]["1"]
            newCorrect += gold[tag]["1"]
    precision = 0.0
    if newGuessed > 0: precision = float(newCorrect)/float(newGuessed)
    recall = 0.0
    if goldTotal > 0: recall = float(newCorrect)/float(goldTotal)
    f1 = 0.0
    if precision > 0.0 and recall > 0.0: 
        f1 = 2*precision*recall/(precision+recall)
    print "%s %0.1f %0.1f %0.1f" % (threshold,100*precision,100*recall,100*f1)

sys.exit()
