#!/usr/bin/python -W all
"""
    ranSelect.py: show data from a random line of a csv file
    usage: ranSelect.py < file.csv
    20170501 erikt(at)xs4all.nl
"""

import cgi
import cgitb
import csv
import random
import re
import sys

COMMAND = sys.argv.pop(0)
# store error log messages in file /tmp/command.log
#cgitb.enable(display=0, logdir="/tmp/"+COMMAND)
cgitb.enable()
DATADIR = "/home/cloud/projects/online-behaviour/machine-learning"
DATAFILE = "dutch-2012.train.csv"
ANNOFILE = "ANNOTATIONS"
IDCOLUMN = 0
USERCOLUMN = 2
TWEETCOLUMN = 4
RETWEETCOLUMN = 5
CLASSCOLUMN = 9
HASHEADING = False
CLASSES = ["Campaign Trail","Campaign Promotion","Campaign Action","Call to Vote","News/Report","Own/Party Stance","Critique","Requesting Input","Advice/Helping","Acknowledgement","Personal","Other","Unknown"]

correct = 0
wrong = 0

# read the data from training or test file
def readData(idColumn,tweetColumn,replyColumn,classColumn,userColumn,fileHasHeading):
    ids = [] # list with tweet ids
    text = [] # list with tweet texts
    users = [] # list with users
    replies = [] # list with ids of replied tweets
    classes = [] # list with tweet classes
    id2index = {} # dictionary linking tweet ids to indexes
    fileName = DATADIR+"/"+DATAFILE
    with open(fileName,"r") as csvfile:
        csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
        lineNbr = 0
        for row in csvreader:
            lineNbr += 1
            # ignore first line if it is a heading
            if lineNbr == 1 and fileHasHeading: continue
            # add tweet text to list
            text.append(row[tweetColumn])
            # add tweet text to list
            users.append(row[userColumn])
            # add tweet class to list
            classes.append(row[classColumn])
            # add reply id to list (if any)
            replies.append(row[replyColumn])
            # link tweet id with list index
            id2index[row[idColumn]] = len(ids)
            # add tweet id to list
            ids.append(row[idColumn])
        csvfile.close()
    # return results
    return({"text":text, "classes":classes, "ids":ids, "replies":replies, "users":users, "id2index":id2index})

# cgi output initialization line
print "Content-Type: text/html\n\n<html><head><title>TITLE</title><meta charset=\"UTF-8\"></head><body>"

# read the data
readDataResults = readData(IDCOLUMN,TWEETCOLUMN,RETWEETCOLUMN,CLASSCOLUMN,USERCOLUMN,HASHEADING)

# process the cgi data if any
form = cgi.FieldStorage()
if "id" in form:
    goldClass = readDataResults["classes"][readDataResults["id2index"][form["id"].value]]
    annotatedClass = form["class"].value
    tweet = readDataResults["text"][readDataResults["id2index"][form["id"].value]]
    correct = int(form["correct"].value)
    wrong = int(form["wrong"].value)
    user = form["user"].value
    thisId = form["id"].value
    if annotatedClass == goldClass: 
        print "<font color=\"green\">"
        correct += 1
    else:
        print "<font color=\"red\">"
        wrong += 1
    contextLink = "<a target = \"_blank\" href=\"https://twitter.com/"+user+"/status/"+thisId+"\">context</a>"
    print "Antwoord: %s; Correct: %s; Tweet: %s %s %s" % (annotatedClass,goldClass,thisId,tweet,contextLink)
    print "</font>\n"
    if correct+wrong > 0:
        print "<br>Correct: %0.1f%%" % (100.0*float(correct)/float(correct+wrong))
    print "<hr>"
    # write annotation to logfile
    try: outFile = open(DATADIR+"/"+ANNOFILE,"a")
    except: sys.exit(COMMAND+": cannot write logfile "+DATADIR+"/"+ANNOFILE)
    print >>outFile,"%s %s %s" % (thisId,goldClass,annotatedClass)
    outFile.close()

index = int(float(len(readDataResults["text"]))*random.random())

# check if the current tweet is a reply 
replyId = readDataResults["replies"][index]
replyTexts = []
while replyId != "None":
    if not replyId in readDataResults["id2index"]: break
    rIndex = readDataResults["id2index"][replyId]
    replyTexts.append("["+readDataResults["classes"][rIndex]+"] "+readDataResults["text"][rIndex])
    replyId = readDataResults["replies"][rIndex]
if len(replyTexts) > 0:
    print "<div style=\"background:#eeeeee; color:blue\">"
    for i in range(0,len(replyTexts)):
        if (i > 0): print "<br>"
        for j in range(i,len(replyTexts)): print "&nbsp;&nbsp;&nbsp;"
        print replyTexts[i]
    print "</div>"
contextLink = "<a target = \"_blank\" href=\"https://twitter.com/"+readDataResults["users"][index]+"/status/"+readDataResults["ids"][index]+"\">context</a>"
# show tweet
print "%s %s" % (readDataResults["text"][index],contextLink)

print "<form>"
print "<input type=\"hidden\" name=\"id\" value=\"%s\">" % (readDataResults["ids"][index])
print "<input type=\"hidden\" name=\"user\" value=\"%s\">" % (readDataResults["users"][index])
print "<input type=\"hidden\" name=\"correct\" value=\"%s\">" % (correct)
print "<input type=\"hidden\" name=\"wrong\" value=\"%s\">" % (wrong)
for i in range(0,len(CLASSES)):
    print "<br><input name=\"class\" type=\"submit\" value=\"%d\" style=\"width:70px;\"> %s" % (i+1,CLASSES[i])
print "</form>"

# done
sys.exit()
