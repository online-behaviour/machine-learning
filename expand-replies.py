#!/usr/bin/python -W all
# expand-replies: combine text of replies with text they are replying on
# usage: expand-replies.py -t text-file -r replies-file [-s skip-file]
# note: csv file formats:
# - text-file and skip-file: column 0: id; 4: text
# - replies-file: column 0: id; 1: reply-to-id; 3: text
# 20170831 erikt(@)xs4all.nl

import csv
import getopt
import naiveBayes
import sys

#COMMAND = sys.argv.pop(0)
USAGE = "usage: "+naiveBayes.COMMAND+"-t text-file -r replies-file [-s skip-file]"

textFile = ""
repliesFile = ""
skipFile = ""
try: options = getopt.getopt(sys.argv,"t:r:s:",[])
except: sys.exit(usage)
for option in options[0]:
    if option[0] == "-t": textFile = option[1]
    elif option[0] == "-r": repliesFile = option[1]
    elif option[0] == "-s": skipFile = option[1]
if textFile == "" or repliesFile == "": sys.exit(USAGE)

texts = []
with open(textFile,"rb") as csvfile:
    csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
    for row in csvreader:
        if len(row) < 10: sys.exit(COMMAND+": incomplete line: "+line)
        thisId = row[0]
        text = " ".join(naiveBayes.tokenize([row[4]],False)[0])
        thisClass = row[9]
        texts.append({"id":thisId,"text":text,"class":thisClass})
    csvfile.close()

print(texts[0])
sys.exit()

replies = []
with open(repliesFile,"rb") as csvfile:
    csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
    for row in csvreader:
        if len(row) < 4: sys.exit(COMMAND+": incomplete line: "+line)
        thisId = row[0]
        repliedToId = row[1]
        text = " ".join(naiveBayes.tokenize([row[3]],False)[0])
        replies.append({"id":thisId,"replied-to-id":repliedToId,"text":text})
    csvfile.close()

