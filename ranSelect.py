#!/usr/bin/python -W all
"""
    ranSelect.py: show data from a random line of a csv file
    usage: ranSelect.py < file.csv
    20170501 erikt(at)xs4all.nl
"""

import cgi
import cgitb
import csv
import os
import random
import re
import sys

COMMAND = sys.argv.pop(0).split("/")[-1]
# store error log messages in file /tmp/command.log
#cgitb.enable(display=0, logdir="/tmp/"+COMMAND)
cgitb.enable()
DATADIR = "/home/cloud/projects/online-behaviour/machine-learning"
DATAFILE = "dutch-2012.csv.unique"
ANNOFILE = "ANNOTATIONS."+COMMAND
IDCOLUMN = 0
USERCOLUMN = 2
TWEETCOLUMN = 4
RETWEETCOLUMN = 5
CLASSCOLUMN = 9
HASHEADING = False
CLASSES = ["Campaign Trail","Campaign Promotion","Campaign Action","Call to Vote","News/Report","Own/Party Stance","Critique","Requesting Input","Advice/Helping","Acknowledgement","Personal","Other","Unknown"]

correct = 0
wrong = 0
processed = {}
annotate8 = True

# read annotations file
def readAnnotations(fileName):
    global processed
    try: inFile = open(fileName,"r")
    except: sys.exit(COMMAND+": cannot read file "+fileName)
    for line in inFile:
        line = line.rstrip()
        fields = line.split()
        if len(line) < 3: sys.exit(COMMAND+": unexpected line in file "+fileName+": "+line)
        processed[fields[0]] = True

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
            thisId = row[idColumn]
            thisClass = row[classColumn]
            # only keep unannotated tweets of class 8
            if not thisId in processed and (not annotate8 or thisClass == "8"):
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

def selectTweet():
   global readDataResults
   index = int(float(len(readDataResults["text"]))*random.random())
   while annotate8 and \
       (readDataResults["classes"][index] != "8" or readDataResults["ids"][index] in processed.keys()):
       index = int(float(len(readDataResults["text"]))*random.random())
   return(index)

# cgi output initialization line
print "Content-Type: text/html\n\n<html><head><title>annotate</title><meta charset=\"UTF-8\"></head><body>"

# read the known annotations
readAnnotations(DATADIR+"/"+ANNOFILE)

# read the data
readDataResults = readData(IDCOLUMN,TWEETCOLUMN,RETWEETCOLUMN,CLASSCOLUMN,USERCOLUMN,HASHEADING)

# process the cgi data if any
form = cgi.FieldStorage()
if "id" in form:
    goldClass = readDataResults["classes"][readDataResults["id2index"][form["id"].value]]
    annotatedClass = form["class"].value
    tweet = readDataResults["text"][readDataResults["id2index"][form["id"].value]]
    if "correct" in form: correct = int(form["correct"].value)
    if "wrong" in form: wrong = int(form["wrong"].value)
    user = form["user"].value
    thisId = form["id"].value
    if "ANNOTATE8" in form.keys(): annotate8 = True
    else: annotate8 = False
    print "<font color=\"green\">"
    # correct += 1
    processed[thisId] = True
    contextLink = "<a target = \"_blank\" href=\"https://twitter.com/"+user+"/status/"+thisId+"\">context</a>"
    print "Antwoord: %s; Tweet: %s %s %s" % (annotatedClass,thisId,tweet,contextLink)
    print "</font>\n"
#   if correct+wrong > 0:
#       print "<br>Correct: %0.1f%%" % (100.0*float(correct)/float(correct+wrong))
    print "<hr>"
    # write annotation to logfile
    try: outFile = open(DATADIR+"/"+ANNOFILE,"a")
    except: sys.exit(COMMAND+": cannot write logfile "+DATADIR+"/"+ANNOFILE)
    print >>outFile,"%s %s %s %s" % (thisId,goldClass,annotatedClass,os.environ["REMOTE_ADDR"])
    outFile.close()

# check if all tweets have been processed
if len(readDataResults["text"]) <= 1:
    print "Klaar"
    sys.exit()
index = selectTweet()
if readDataResults["text"][index] in processed.keys():
    print "duplicate id: %s" % (index)
    sys.exit()

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
if annotate8: sys.stdout.write(str(1+len(processed))+": ")
print "%s %s" % (readDataResults["text"][index],contextLink)

print "<form>"
print "<input type=\"hidden\" name=\"id\" value=\"%s\">" % (readDataResults["ids"][index])
print "<input type=\"hidden\" name=\"user\" value=\"%s\">" % (readDataResults["users"][index])
#print "<input type=\"hidden\" name=\"correct\" value=\"%s\">" % (correct)
#print "<input type=\"hidden\" name=\"wrong\" value=\"%s\">" % (wrong)
if annotate8: print "<input type=\"hidden\" name=\"ANNOTATE8\" value=\"1\">"
print "<table cellspacing=\"20px\">"
for i in range(0,len(CLASSES)):
    if 2*int(i/2) == int(i): print "<tr><td>"
    else: print "<td>"
    print "<input name=\"class\" type=\"submit\" value=\"%d\" style=\"width:100px;\"> %s" % (i+1,CLASSES[i])
print """
</table>
</form>
<hr>
<font size="1">
<h3>Instructies</h3>
<ol>
<li> Lees de tweet
<li> Kies de meest geschikte klasse en klik op de button met het cijfer van deze klasse
<li> Als de klasse niet duidelijk is, klik dan op <font color="blue"><u>context</u></font> achter de tweet om de context te bekijken
<li> Als je een fout maakt, kies dan BACK in de browser om terug te gaan naar de vorige tweet
<li> Het nummer voor de tweet geeft aan de hoeveelste tweet nu in beeld staat (er zijn er 8575)
</ol>
</font>
</body>
</html>
"""

# done
sys.exit()
