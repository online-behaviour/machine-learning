#!/usr/bin/python3 -W all
# expand-replies: combine text of replies with text they are replying on
# usage: expand-replies.py -t tweet-file.csv -r replies-file.csv [-s skip-file.csv]
# note: csv file formats:
# - tweet-file.csv and skip-file.csv: column 0: id; 4: text; 9: label
# - replies-file.csv: column 0: id; 1: reply-to-id; 4: text
# 20170831 erikt(@)xs4all.nl

import csv
import getopt
import nltk
import re
import sys

COMMAND = sys.argv.pop(0)
USAGE = "usage: "+COMMAND+"-t tweet-file -r replies-file [-s skip-file]"

def tokenize(text,keepUpperCase):
    tokenizedText = []   # list of lists of tokens per tweet
    patternEmail = re.compile("\S+@\S+")
    patternUserref = re.compile("@\S+")
    patternUrl = re.compile("http\S+")
    for i in range(0,len(text)):
        # convert tweet text to lower case 
        if not keepUpperCase: text[i] = text[i].lower()
        # collapse all mail addresses, urls and user references to one token
        text[i] = patternEmail.sub("MAIL",text[i])
        text[i] = patternUserref.sub("USER",text[i])
        text[i] = patternUrl.sub("HTTP",text[i])
        # tokenize the tweet
        tokenizedText.append(nltk.word_tokenize(text[i]))
    return(tokenizedText)

def readTweets(fileName):
    tweets = []
    ids = {}
    with open(fileName,"r",encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
        for row in csvreader:
            if len(row) < 5: sys.exit(COMMAND+": unexpected input line: "+str(row))
            thisId = row[0]
            text = " ".join(tokenize([row[4]],False)[0])
            thisClass = "None"
            if len(row) > 9: thisClass = row[9]
            tweets.append({"id":thisId,"text":text,"class":thisClass})
            ids[thisId] = thisClass
        csvfile.close()
    return({"tweets":tweets,"ids":ids})

def readReplies(fileName):
    replies = {}
    with open(fileName,"r",encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
        for row in csvreader:
            if len(row) < 5: sys.exit(COMMAND+": incomplete line: "+str(row))
            thisId = row[0]
            replyToId = row[1]
            text = " ".join(tokenize([row[4]],False)[0])
            replies[thisId] = {"reply-to-id":replyToId,"text":text}
        csvfile.close()
    return(replies)

def main(argv):
    tweetFile = ""
    repliesFile = ""
    skipFile = ""
    try: options = getopt.getopt(sys.argv,"t:r:s:",[])
    except: sys.exit(usage)
    for option in options[0]:
        if option[0] == "-t": tweetFile = option[1]
        elif option[0] == "-r": repliesFile = option[1]
        elif option[0] == "-s": skipFile = option[1]
    if tweetFile == "" or repliesFile == "": sys.exit(USAGE)
    
    readTweetsResults = readTweets(tweetFile)
    tweets = readTweetsResults["tweets"]
    classes = readTweetsResults["ids"]
    replies = readReplies(repliesFile)
    skipTweets = {}
    if skipFile != "": skipTweets = readTweets(skipFile)["ids"]
    
    nbrOfClusters = 0
    nbrOfPure = 0
    for t in range(0,len(tweets)):
        thisId = tweets[t]["id"]
        if not thisId in skipTweets:
            thisClass = tweets[t]["class"]
            cluster = 1
            pure = True
            while thisId in replies and replies[thisId]["reply-to-id"] != "" \
                and replies[thisId]["reply-to-id"] != "None":
                tweets[t]["text"] += " REPLYTO"
                if replies[thisId]["reply-to-id"] in skipTweets: 
                    thisId = "STOP!"
                else: 
                    cluster += 1
                    thisId = replies[thisId]["reply-to-id"]
                    if thisId in classes and classes[thisId] != thisClass: pure = False
                if thisId in replies:
                    tweets[t]["text"] += " "+replies[thisId]["text"]
            print("__label__"+tweets[t]["class"]+" "+tweets[t]["text"])
            if cluster > 1:
                nbrOfClusters += 1
                if pure: nbrOfPure += 1
    sys.stderr.write("Found "+str(nbrOfClusters)+ " clusters; pure: "+str(nbrOfPure)+" ("+str(int(100*nbrOfPure/nbrOfClusters))+"%)\n")

if __name__ == "__main__":
    sys.exit(main(sys.argv))
