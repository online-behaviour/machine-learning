#!/usr/bin/python -W all
"""
wordProfiles.py: compute word frequencies per output class
usage: wordProfiles.py -t tweetColumn -c classColumn < file
20170609 erikt(at)xs4all.nl
"""

import csv
import getopt
import naiveBayes
import re
import sys

# definition constant
COMMAND = naiveBayes.COMMAND
NONE = -1
USAGE = COMMAND+": -t tweetColumn -c classColumn < file"
# definition variables
tweetColumn = NONE
classColumn = NONE
wordFreq = {}
classes = {}

def countWords(tweetColumn,classColumn):
    classes = {}
    wordFreq = {}
    csvreader = csv.reader(sys.stdin,delimiter=',',quotechar='"')
    for row in csvreader:
        if len(row) < tweetColumn or len(row) < classColumn:
            sys.exit(COMMAND+": unexpected line in file "+fileName+": "+(",".join(row))+"\n")
        tokenized = naiveBayes.tokenize([row[tweetColumn-1]])
        thisClass = row[classColumn-1]
        if thisClass in classes: classes[thisClass] += 1
        else: classes[thisClass] = 1
        words = {}
        for word in tokenized[0]: words[word] = True
        for word in words:
            if not word in wordFreq: wordFreq[word] = {}
            if thisClass in wordFreq[word]: wordFreq[word][thisClass] += 1
            else: wordFreq[word][thisClass] = 1
    return({"wordFreq":wordFreq,"classes":classes})

def compare(x,y):
    return(int(x)-int(y))

def main(argv):
    global tweetColumn
    global classColumn
    # process command line arguments
    try: options = getopt.getopt(argv,"t:c:",[])
    except: sys.exit(USAGE)
    for option in options[0]:
        if   option[0] == "-t": tweetColumn = int(option[1])
        elif option[0] == "-c": classColumn = int(option[1])
    if tweetColumn < 0 or classColumn < 0: sys.exit(USAGE)
    # read csv data from file 2, return as dictionary: file2[key] = value
    countWordsResults = countWords(tweetColumn,classColumn)
    wordFreq = countWordsResults["wordFreq"]
    classes = countWordsResults["classes"]
    for word in wordFreq:
        total = 0
        for thisClass in sorted(classes,cmp=compare):
            if not thisClass in wordFreq[word]: wordFreq[word][thisClass] = 0
            total += wordFreq[word][thisClass]
        sys.stdout.write(str(total))
        for thisClass in sorted(classes,cmp=compare):
            number = str(float(int(1000*wordFreq[word][thisClass]/classes[thisClass]))/1000.0)
            while len(number) < 5: number += "0"
            sys.stdout.write(" "+number)
        print " "+word.encode("utf8")

if __name__ == "__main__":
    sys.exit(main(sys.argv))
