#!/usr/bin/python -W all
"""
   average.py: compute the average of a sequence of numbers
   usage: average.py < file
   20170627 erikt(at)xs4all.nl
"""

import re
import sys

COMMAND = sys.argv.pop(0)

total = 0
count = 0
patternIsNumber = re.compile("^[0-9]+(\.[0-9]+)?$")
for line in sys.stdin:
    line = line.rstrip()
    fields = line.split()
    for n in fields:
        if not patternIsNumber.match(n):
            sys.exit(COMMAND+": "+n+" is not a number\n")
        total += float(n)
        count += 1
print "average: %0.3f" % (total/count)
