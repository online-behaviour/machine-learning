#!/usr/bin/python3 -W all
# expand-replies: combine text of replies with text they are replying on
# usage: expand-replies.py -t tweet-file.csv -r replies-file.csv [-s skip-file.csv] [-i id-col] [-T text-col] [-c class-col] [-u username-col] [-h]
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
EMPTY = ""
IDCOL = 0
USERNAMECOL = 2
TEXTCOL = 4
CLASSCOL = 9
REPLYTOIDCOL = 1
HEADING = False

def tokenize(text,keepUpperCase,keepMailUserHttp):
    tokenizedText = []   # list of lists of tokens per tweet
    patternEmail = re.compile("\S+@\S+")
    patternUserref = re.compile("@\S+")
    patternUrl = re.compile("http\S+")
    for i in range(0,len(text)):
        # convert tweet text to lower case 
        if not keepUpperCase: text[i] = text[i].lower()
        # collapse all mail addresses, urls and user references to one token
        if not keepMailUserHttp:
            text[i] = patternEmail.sub("MAIL",text[i])
            text[i] = patternUserref.sub("USER",text[i])
            text[i] = patternUrl.sub("HTTP",text[i])
        # tokenize the tweet
        tokenizedText.append(nltk.word_tokenize(text[i]))
    return(tokenizedText)

def readTweets(fileName,classCol,idCol,textCol,usernameCol,heading):
    tweets = []
    ids = {}
    count = 0
    with open(fileName,"r",encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
        for row in csvreader:
            if len(row) <= textCol: sys.exit(COMMAND+": unexpected input line: "+str(row))
            count += 1
            if not heading or count != 1:
                thisId = row[idCol]
                userName = row[usernameCol]
                text = row[textCol].replace("\n"," ")
                tokenizedText = " ".join(tokenize([text],False,False)[0])
                thisClass = "None"
                if len(row) > classCol: thisClass = row[classCol]
                tweets.append({"id":thisId,"text":text,"userName":userName,"tokenizedText":tokenizedText,"class":thisClass})
                ids[thisId] = thisClass
        csvfile.close()
    return({"tweets":tweets,"ids":ids})

def readReplies(fileName,idCol,replytoidCol,textCol):
    replies = {}
    with open(fileName,"r",encoding="utf8") as csvfile:
        csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
        for row in csvreader:
            if len(row) <= textCol: sys.exit(COMMAND+": incomplete line: "+str(row))
            thisId = row[idCol]
            replyToId = row[replytoidCol]
            text = row[textCol]
            tokenizedText = " ".join(tokenize([text],False,False)[0])
            replies[thisId] = {"reply-to-id":replyToId,"text":text,"tokenizedText":tokenizedText}
        csvfile.close()
    return(replies)

def main(argv):
    tweetFile = EMPTY
    repliesFile = EMPTY
    skipFile = EMPTY
    idCol = IDCOL
    usernameCol = USERNAMECOL
    textCol = TEXTCOL
    classCol = CLASSCOL
    replytoidCol = REPLYTOIDCOL
    heading = HEADING
    try: options = getopt.getopt(sys.argv,"c:hi:r:s:t:T:u:",[])
    except: sys.exit(USAGE)
    for option in options[0]:
        if option[0] == "-c": classCol = int(option[1])-1
        elif option[0] == "-h": heading = True
        elif option[0] == "-i": idCol = int(option[1])-1
        elif option[0] == "-r": repliesFile = option[1]
        elif option[0] == "-s": skipFile = option[1]
        elif option[0] == "-t": tweetFile = option[1]
        elif option[0] == "-T": textCol = int(option[1])-1
        elif option[0] == "-u": usernameCol = int(option[1])-1
        else: sys.exit(COMMAND+": unknown option "+option[0])
    if tweetFile == "" or repliesFile == "": sys.exit(USAGE)
    
    readTweetsResults = readTweets(tweetFile,classCol,idCol,textCol,usernameCol,heading)
    tweets = readTweetsResults["tweets"]
    classes = readTweetsResults["ids"]
    replies = readReplies(repliesFile,idCol,replytoidCol,textCol)
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
            print("__label__"+tweets[t]["class"]+" ID="+tweets[t]["id"]+" SENDER="+tweets[t]["userName"]+" "+tweets[t]["tokenizedText"]+" RAWTEXT "+tweets[t]["text"])
            if cluster > 1:
                nbrOfClusters += 1
                if pure: nbrOfPure += 1
    if nbrOfClusters > 0:
        sys.stderr.write("Found "+str(nbrOfClusters)+ " clusters; pure: "+str(nbrOfPure)+" ("+str(int(100*nbrOfPure/nbrOfClusters))+"%)\n")

if __name__ == "__main__":
    sys.exit(main(sys.argv))
