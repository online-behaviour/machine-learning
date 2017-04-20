#!/usr/bin/python -W all
# eval: compute precision and recall for classifier output
# usage: eval < file
# note: expects gold tag and guessed tag as final two tokens on line
# 20170413 erikt(at)xs4all.nl

import re
import sys

ALL = ""     # tag representing all counts

correct = {} # dictionary with correct counts
gold = {}    # dictionary with gold tag counts
guessed = {} # dictionary with guessed tag counts
correct[ALL] = 0
gold[ALL] = 0
guessed[ALL] = 0

for line in sys.stdin:
    # remove final newline
    line = line.rstrip()
    # get the tokens on the line
    tokens = line.split()
    # check if the line contains at least two tokens
    if len(tokens) <= 1: continue
    # get gold tag and guessed tag
    guessedTag = tokens.pop(-1)
    goldTag = tokens.pop(-1)
    # check if the guess is correct
    if guessedTag == goldTag:
        if goldTag in correct: correct[goldTag] += 1
        else: correct[goldTag] = 1
        correct[ALL] += 1
    # add the gold tag to the counts
    if goldTag in gold: gold[goldTag] += 1
    else: gold[goldTag] = 1
    # add the guessed tag to the counts
    if guessedTag in guessed: guessed[guessedTag] += 1
    else: guessed[guessedTag] = 1
    # add the occurrance to the overall counts
    gold[ALL] += 1
    guessed[ALL] += 1

# show results
for tag in sorted(gold.iterkeys()):
    if not tag in correct: correct[tag] = 0.0
    if not tag in guessed: guessed[tag] = 0.0
    if guessed[tag] > 0.0: precision = float(correct[tag])/float(guessed[tag])
    else: precision = 0.0
    if gold[tag] > 0.0: recall = float(correct[tag])/float(gold[tag])
    else: recall = 0.0
    if precision > 0.0 and recall > 0.0: 
        f1 = 2*precision*recall/(precision+recall)
    else: f1 = 0.0
    print "%5d %5.1f %5.1f %5.1f %s" % (gold[tag],100*precision,100*recall,100*f1,tag)

sys.exit()
