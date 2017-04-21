#!/usr/bin/python -W all
# confusion: compute confusion matrix
# usage: confusion gold-column-number guessed-column-number < file
# note: expects space-separated file
# 20170421 erikt(at)xs4all.nl

import re
import sys

COMMAND = sys.argv.pop(0)
if len(sys.argv) != 2: sys.exit("usage: "+COMMAND+" gold-column-number guessed-column-number < file\n")
GOLDCOLUMN = int(sys.argv.pop(0))
GUESSEDCOLUMN = int(sys.argv.pop(0))

nbrOfClasses = {} # count per class
confusion = {} # confusion matrix: guesses per gold tag

# process classifications
for line in sys.stdin:
    # remove final newline
    line = line.rstrip()
    # get the tokens on the line
    tokens = line.split()
    # sanity check
    if (len(tokens) < GOLDCOLUMN) or (len(tokens) < GUESSEDCOLUMN):
        sys.exit(COMMAND+": input line contains too few tokens: "+line+"\n")
    # count gold tag
    gold = tokens[GOLDCOLUMN-1]
    if gold in nbrOfClasses: nbrOfClasses[gold] += 1
    else:
        nbrOfClasses[gold] = 1
        confusion[gold] = {}
    # add guess tag to counts, if necessary
    guess = tokens[GUESSEDCOLUMN-1]
    if not guess in nbrOfClasses: 
        nbrOfClasses[guess] = 0
        confusion[guess] = {}
    # add guess to confusion matrix
    if guess in confusion[gold]: confusion[gold][guess] += 1
    else: confusion[gold][guess] = 1

# show confusion matrix
patternFourChars = re.compile("....")
for gold in sorted(nbrOfClasses,key=nbrOfClasses.get,reverse=True):
    # pretty print: create output string of at least four characters
    outString = str(gold)
    while not patternFourChars.match(outString): outString = " "+outString
    sys.stdout.write(outString+":")
    for guess in sorted(nbrOfClasses,key=nbrOfClasses.get,reverse=True):
        if gold in confusion and guess in confusion[gold]:
            # pretty print: create output string of at least four characters
            outString = str(confusion[gold][guess])
            while not patternFourChars.match(outString): outString = " "+outString
            sys.stdout.write(" "+outString)
        # just print a period for unseen gold-guessed combinations
        else: sys.stdout.write("    .")
    # print a newline character to end this output line
    print

# done
sys.exit()
