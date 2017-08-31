#!/usr/bin/python -W all
"""
    tokenizeTweets.py: tokenize tweets from csv file for future processing
    usage: tokenizeTweets [ -c column-id ][ [ -h ] < file.csv
    20170523 erikt(at)xs4all.nl
"""

import csv
import getopt
import naiveBayes
import sys

#COMMAND = sys.argv.pop(0)
tweetColumn = 0
fileHasHeading = False

# check for command line options
def checkOptions():
    global tweetColumn
    global fileHasHeading

    try: (opts,args) = getopt.getopt(sys.argv,"c:h",[])
    except: sys.exit(USAGE)
    for option in opts:
        if option[0] == "-c": tweetColumn = int(option[1])
        elif option[0] == "-h": fileHasHeading = True
    return(args) # return remaining command line arguments

# read csv data from stdin and tokenize it
def readData(tweetColumn,fileHasHeading):
    text = []
    csvreader = csv.reader(sys.stdin,delimiter=',',quotechar='"')
    lineNbr = 0
    for row in csvreader:
        lineNbr += 1
        # ignore first line if it is a heading
        if lineNbr == 1 and fileHasHeading: continue
        # tokenize text
        tokenized = naiveBayes.tokenize([row[tweetColumn]],False)
        # print tokenized text
        for i in range(0,len(tokenized)):
            outLine = ""
            for j in range(0,len(tokenized[i])):
                outLine += tokenized[i][j]
                if j < len(tokenized[i])-1: outLine += " "
            print (unicode(outLine).encode('utf8'))
            # flush stdout
            sys.stdout.flush()
    return(text)

# process command line arguments
checkOptions()
# read csv data from stdin
text = readData(tweetColumn,fileHasHeading)

