#!/usr/bin/python3 -W all
# compare-dependent.py: compare two dependent experiments
# usage: compare-dependent exp1 exp2 < score-file
# note: score-file contains lines with starting with exp1/exp2, ending with score
# 20170914 erikt(at)xs4all.nl

import sys

COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+" exp1 exp2 < score-file"

if len(sys.argv) < 2: sys.exit(USAGE)
exp1 = sys.argv.pop(0)
exp2 = sys.argv.pop(0)

exp1seen = False
exp2seen = False
score1 = 0
score2 = 0
lastExp = ""
for line in sys.stdin:
    line = line.rstrip()
    fields = line.split()
    exp = fields.pop(0)
    score = float(fields.pop(-1))
    if exp == exp1:
        if lastExp != exp1 and exp1seen and exp2seen:
            print(str(score1-score2))
            exp1seen = False
            exp2seen = False
        exp1seen = True
        score1 = score
        lastExp = exp1
    elif exp == exp2:
        if lastExp != exp2 and exp1seen and exp2seen:
            print(str(score1-score2))
            exp1seen = False
            exp2seen = False
        exp2seen = True
        score2 = score
        lastExp = exp2

if exp1seen and exp2seen: print(str(score1-score2))
