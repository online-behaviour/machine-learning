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
DATADIR = "/WWW/t/tjongkim/private/machine-learning"
DATAFILE = "active" # "dutch-2012.csv.8.questionmark" # 13"
ANNOFILE = "ANNOTATIONS."+COMMAND
# -1,6,0.991,7,0.901,674221988416720896,JoelVoordewind,Terecht zegt VdSteur dat daders moeten worden aangepakt na bedreigingen LHBTs en op voorspraak v CU vult hij aan ook christen-asielzoekers.
IDCOLUMN = 5 # was 0
USERCOLUMN = 6 # was 2
TWEETCOLUMN = 7 # was 4
RETWEETCOLUMN = -1 # was 5
CLASSCOLUMN = 0 # was 9
HASHEADING = False
CLASSES = ["Campaign Trail","Campaign Promotion","Campaign Action","Call to Vote","News/Report","Own/Party Stance","Critique","Requesting Input","Advice/Helping","Acknowledgement","Personal","Other","Unknown"]

correct = 0
wrong = 0
processed = {}
annotate8 = False
lastProcessed = ""

# read annotations file
def readAnnotations(fileName):
    global processed
    global lastProcessed
    try: inFile = open(fileName,"r")
    except: sys.exit(COMMAND+": cannot read file "+fileName)
    for line in inFile:
        line = line.rstrip()
        fields = line.split()
        if len(line) < 3: sys.exit(COMMAND+": unexpected line in file "+fileName+": "+line)
        lastProcessed = fields[0]
        processed[lastProcessed] = True

# read the data from training or test file
def readData(idColumn,tweetColumn,replyColumn,classColumn,userColumn,fileHasHeading):
    ids = [] # list with tweet ids
    text = [] # list with tweet texts
    users = [] # list with users
    replies = [] # list with ids of replied tweets
    classes = [] # list with tweet classes
    guesses = [] # list with guesses of classes
    id2index = {} # dictionary linking tweet ids to indexes
    twitterIds = [] # list with twitter ids
    fileName = DATADIR+"/"+DATAFILE
    inFile = open(fileName,"r")
    lineNbr = 0
    for line in inFile:
        lineNbr += 1
        thisId = str(lineNbr)
        line = line.rstrip()
        fields = line.split()
        thisGuess = fields.pop(0)
        thisClass = fields.pop(0)
        twitterId = fields[0]
        twitterId = re.sub(r"ID=","",twitterId) 
        line = " ".join(fields)
        # only keep unannotated tweets and the last one that was annotated
        if (not thisId in processed or thisId == lastProcessed) and \
           (not annotate8 or thisClass == "__label__8"):
           # add tweet text to list
           text.append(line)
           # add user to list
           users.append("UNKNOWN")
           # add tweet class to list
           classes.append(thisClass)
           guesses.append(thisGuess)
           # add reply id to list (if any)
           replies.append("UNKNOWN")
           # link tweet id with list index
           id2index[thisId] = len(ids)
           # add tweet id to list
           ids.append(thisId)
           twitterIds.append(twitterId)
    inFile.close()
    # return results
    return({"text":text, "classes":classes, "guesses":guesses,"ids":ids, "replies":replies, "users":users, "id2index":id2index, "twitterIds":twitterIds})

def selectTweet():
   global readDataResults
   index = int(float(len(readDataResults["text"]))*random.random())
   while annotate8 and \
       (readDataResults["classes"][index] != "8" or readDataResults["ids"][index] in processed.keys()):
       index = int(float(len(readDataResults["text"]))*random.random())
   return(index)

# remove tweet with id thisId from readDataResults
def deleteTweet(thisId):
    global readDataResults
    readDataResults["id2index"][readDataResults["ids"][-1]] = readDataResults["id2index"][thisId]
    readDataResults["text"][readDataResults["id2index"][thisId]] = readDataResults["text"][-1]
    readDataResults["text"].pop(-1)
    readDataResults["classes"][readDataResults["id2index"][thisId]] = readDataResults["classes"][-1]
    readDataResults["classes"].pop(-1)
    readDataResults["ids"][readDataResults["id2index"][thisId]] = readDataResults["ids"][-1]
    readDataResults["ids"].pop(-1)
    readDataResults["replies"][readDataResults["id2index"][thisId]] = readDataResults["replies"][-1]
    readDataResults["replies"].pop(-1)
    readDataResults["users"][readDataResults["id2index"][thisId]] = readDataResults["users"][-1]
    readDataResults["users"].pop(-1)
    readDataResults["id2index"][thisId] = -1

# cgi output initialization line
print "Content-Type: text/html\n\n<html><head><title>annotate</title><meta charset=\"UTF-8\"></head><body>"

# if os.path.isdir("/WWW/t/tjongkim/private/machine-learning"): print("<br>TRUE!")
# else: print("<br>FALSE!")

# read the known annotations
readAnnotations(DATADIR+"/"+ANNOFILE)

# read the data
readDataResults = readData(IDCOLUMN,TWEETCOLUMN,RETWEETCOLUMN,CLASSCOLUMN,USERCOLUMN,HASHEADING)

# process the cgi data if any
form = cgi.FieldStorage()
if "id" in form:
    prevId = form["id"].value
    prevId = readDataResults["id2index"][prevId]
    prevTweetId = readDataResults["twitterIds"][prevId]
    goldClass = readDataResults["classes"][readDataResults["id2index"][form["id"].value]]
    annotatedClass = form["class"].value
    prevTweet = readDataResults["text"][readDataResults["id2index"][form["id"].value]]
    prevTweet = re.sub(".* RAWTEXT ","",prevTweet)
    if "correct" in form: correct = int(form["correct"].value)
    if "wrong" in form: wrong = int(form["wrong"].value)
    user = form["user"].value
    thisId = form["id"].value
    if "ANNOTATE8" in form.keys(): annotate8 = True
    else: annotate8 = False
    if goldClass != "__label__None":
        if "__label__"+annotatedClass == goldClass: 
            correct += 1
        else:
            wrong += 1
    processed[thisId] = True
    # contextLink = "<a target = \"_blank\" href=\"https://twitter.com/user/status/id">context</a>"
    contextLink = ""
    fields = prevTweet.split("REPLYTO")
    fields = fields[::-1]
    if fields[0] == "": fields[0] = "???"
    patternGoldClass = re.compile("__label__")
    goldClassPrint = patternGoldClass.sub("",goldClass)
    if len(fields) > 0: prevTweet = "<br><strong>REPLY</strong> ".join(fields)
    # write annotation to logfile
    try: outFile = open(DATADIR+"/"+ANNOFILE,"a")
    except: sys.exit(COMMAND+": cannot write logfile "+DATADIR+"/"+ANNOFILE)
    print >>outFile,"%s %s %s %s" % (thisId,goldClass,annotatedClass,os.environ["REMOTE_ADDR"])
    outFile.close()
    deleteTweet(thisId)

# we have included the lastProcessed tweet in the data set of remaining tweets
# so that it can be reannotated if the annotator made an error
# now remove it again to avoid selecting it for a second time
if lastProcessed != "": deleteTweet(lastProcessed)

# check if all tweets have been processed
if len(readDataResults["text"]) <= 0:
    if goldClass != "__label__None":
        if "__label__"+annotatedClass == goldClass: 
            print "<font color=\"blue\">"
        else:
            if goldClass != "__label__None": print "<font color=\"red\">"
    print "<hr>"
    print "<div style=\"\">Antwoord: %s; Correct: %s; Tweet: %s %s</div>" % (annotatedClass,goldClassPrint,prevTweet,contextLink)
    if goldClass != "__label__None": print "</font>\n"
    if correct+wrong > 0:
        print "<br>Correct: %0.1f%%" % (100.0*float(correct)/float(correct+wrong))
    print "<p>Klaar"
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
contextLink = "<a target = \"_blank\" href=\"https://twitter.com/user/status/"+str(readDataResults["twitterIds"][index])+"\">context</a>"
# show tweet
tweetText = readDataResults["text"][index]
tweetText = re.sub(r".* RAWTEXT","",tweetText)
sys.stdout.write("<div style=\"\">"+str(1+len(processed))+": ")
print "%s %s</div>" % (tweetText,contextLink)

pattern = re.compile("__label__")
readDataResults["guesses"][index] = pattern.sub("",readDataResults["guesses"][index])
print "<form>"
print "<input type=\"hidden\" name=\"id\" value=\"%s\">" % (readDataResults["ids"][index])
print "<input type=\"hidden\" name=\"user\" value=\"%s\">" % (readDataResults["users"][index])
print "<input type=\"hidden\" name=\"correct\" value=\"%s\">" % (correct)
print "<input type=\"hidden\" name=\"wrong\" value=\"%s\">" % (wrong)
if annotate8: print "<input type=\"hidden\" name=\"ANNOTATE8\" value=\"1\">"
print "<table cellspacing=\"20px\">"
for i in range(0,len(CLASSES)):
    if 2*int(i/2) == int(i): print "<tr><td>"
    else: print "<td>"
    if int(readDataResults["guesses"][index])-1 == i: print "<strong style=\"color:red\">"
    print "<input name=\"class\" type=\"submit\" value=\"%d\" style=\"width:100px;\"> %s" % (i+1,CLASSES[i])
    if int(readDataResults["guesses"][index])-1 == i: print "</strong>"
print """
</table>
</form>
<hr>
<font size="1">
<h3>Instructies</h3>
<ol>
<li> Lees de tweet
<li> Kies de meest geschikte klasse en klik op de button met het cijfer van deze klasse
<li> Als je een fout maakt, kies dan BACK in de browser om terug te gaan naar de vorige tweet
<li> Het nummer voor de tweet geeft aan de hoeveelste tweet nu in beeld staat
</ol>
</font>
"""

try:
    if goldClass != "__label__None":
        if "__label__"+annotatedClass == goldClass: 
            print "<font color=\"blue\">"
        else:
            if goldClass != "__label__None": print "<font color=\"red\">"
    contextLink = "<a target = \"_blank\" href=\"https://twitter.com/user/status/"+prevTweetId+"\">context</a>"
    print "<hr>"
    print "<div style=\"\">Antwoord: %s; Correct: %s; Tweet: %s %s</div>" % (annotatedClass,goldClassPrint,prevTweet,contextLink)
    if goldClass != "__label__None": print "</font>\n"
    if correct+wrong > 0:
        print "<br>Correct: %0.1f%%" % (100.0*float(correct)/float(correct+wrong))
except:
    print("")

print """
</body>
</html>
"""

# done
sys.exit()
