#!/usr/bin/python -W all
"""
   average.py: compute the average of a sequence of numbers
   usage: average.py < file
   20170627 erikt(at)xs4all.nl
"""

import math
import re
import sys

COMMAND = sys.argv.pop(0)

interval95 = 1.96

total = 0.0
count = 0.0
numbers = []
pattern = re.compile("^\s*#")
for line in sys.stdin:
    line = line.rstrip()
    if not pattern.match(line):
        fields = line.split()
        for n in fields:
            try:
                nFloat = float(n)
            except:
                sys.exit(COMMAND+": "+n+" is not a number\n")
            total += nFloat
            count += 1.0
            numbers.append(float(n))

if count <= 0.0:
    sys.exit(COMMAND+": could not read any data!")

average = total/count

total = 0.0
for n in numbers: total += (n-average)*(n-average)
sd = math.sqrt(total/count)

print "count: %d; average: %0.3f; sd: %0.3f; deviance: %0.3f" % (int(count),average,sd,sd*interval95)
