#!/usr/bin/python -W all
"""
    naiveBayes.py: run naive bayes experiment
    usage: naiveBayes.py train-file
    20170410 erikt(at)xs4all.nl
"""

import csv
import getopt
import numpy
import re
import sys
from scipy.sparse import csr_matrix
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB

COMMAND = sys.argv[0]
MINFREQ = 5     # minimum frequency of used tokens (rest is dicarded)
TWEETCOLUMN = 4 # column number of tweet text in file dutch-2012.csv
CLASSCOLUMN = 9 # column number of tweeting behaviour (T3) in file dutch-2012.csv
TRAINPART = 0.9 # percentage of the data used as training data; rest is test
OTHER = "O" # other value in binary experiment
if len(sys.argv) < 2: sys.exit("usage: "+COMMAND+" train-file\n")
trainFile = sys.argv[1]
targetClasses = ["1","2","3","4","5","6","7","8","9","10","11","12","13"]
# targetClasses = ["-","+"]

# read the data from the training file
def readData(targetClass):
    text = []
    classes = []
    with open(trainFile,"rb") as csvfile:
        csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
        for row in csvreader: 
            text.append(row[TWEETCOLUMN])
            if row[CLASSCOLUMN] == targetClass: classes.append(row[CLASSCOLUMN])
            else: classes.append(OTHER)
        csvfile.close()
    # throw away first data point: heading
    text.pop(0)
    classes.pop(0)
    # return results
    return({"text":text, "classes":classes})

# tokenize the tweet text
def tokenize(text,maxTrain):
    tokenized = []   # list of lists of tokens per tweet
    tokenIds = {}    # dictionary of ids of tokens in tokenList
    tokenCounts = {} # dictionary with per-token counts in training data
    tokenList = []   # list of all tokens
    patternCharacter = re.compile("(.)")
    patternPunctuation = re.compile("\W")
    patternSpace = re.compile("\s")
    for i in range(0,len(text)):
        # convert tweet text to lower case and split in characters
        tweetChars = list(text[i].lower())
        # build tokens from characters
        tweetTokens = []
        tweetTokenIndex = -1
        insideToken = False
        # examine each character in the tweet
        for c in tweetChars:
           # white space signals the end of a token
           if patternSpace.search(c):
               insideToken = False
           # punctuation characters should be separate unextendable tokens
           elif patternPunctuation.search(c):
               tweetTokenIndex += 1
               tweetTokens.append(c)
               insideToken = False
           # characters [a-z0-9] should be appended to the current token
           elif insideToken:
               tweetTokens[tweetTokenIndex] = tweetTokens[tweetTokenIndex]+c
           # if we are not in a token, start a new one for this [a-z0-9]
           else:
               tweetTokenIndex += 1
               tweetTokens.append(c)
               insideToken = True
        # add the tokens of this tweet to a global token list
        for t in tweetTokens:
            # if the token is unknown
            if not t in tokenIds:
                # add it to the token list with a unique id
                tokenIds[t] = len(tokenList)
                tokenList.append(t)
                # only count tokens in training data
                if i < maxTrain: tokenCounts[t] = 1
                else: tokenCounts[t] = 0
            # only count tokens in training data
            elif i < maxTrain:
                tokenCounts[t] += 1
        # add the tokens of this tweet to a token list
        tokenized.append(tweetTokens)
    return({"tokenized":tokenized,"tokenList":tokenList,"tokenCounts":tokenCounts})

# select tokens as features for vectors
def makeVectors(tokenizeResults,maxTrain):
    # in order to avoid memory problems, we only select the
    # more frequent tokens as features
    selectedTokens = []
    selectedIds = {}
    for i in range(0,len(tokenizeResults["tokenList"])):
       if tokenizeResults["tokenCounts"][tokenizeResults["tokenList"][i]] >= MINFREQ: 
          selectedIds[tokenizeResults["tokenList"][i]] = len(selectedTokens)
          selectedTokens.append(tokenizeResults["tokenList"][i])
    # make a sparse data matrix for the training data
    rows = []
    columns = []
    data = []
    for i in range(0,maxTrain):
        for token in tokenizeResults["tokenized"][i]:
            if token in selectedTokens:
               data.append(1)
               rows.append(i)
               columns.append(selectedIds[token])
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.html
    train = csr_matrix((data,(rows,columns)),shape=(maxTrain,len(selectedTokens)))
    # make a sparse data matrix for the test data
    rows = []
    columns = []
    data = []
    for i in range(maxTrain,len(tokenizeResults["tokenized"])):
        for token in tokenizeResults["tokenized"][i]:
            if token in selectedTokens:
               data.append(1)
               rows.append(i-maxTrain)
               columns.append(selectedIds[token])
    test = csr_matrix((data,(rows,columns)),shape=(len(tokenizeResults["tokenized"])-maxTrain,len(selectedTokens)))
    return({"train":train,"test":test}) 

for targetClass in targetClasses:
    # read the data from the training file
    readDataResults = readData(targetClass)
    # use 90% of the data as train; 10% as test
    # note: the data is assumed to be sorted by time
    maxTrain = int(TRAINPART*len(readDataResults["text"]))
    # tokenize the text in the data
    tokenizeResults = tokenize(readDataResults["text"],maxTrain)
    # convert the text to token vectors (make selection)
    makeVectorsResults = makeVectors(tokenizeResults,maxTrain)
    
    # perform naive bayes experiment
    # alternatives: MultinomialNB() GaussianNB() BernoulliNB()
    # first: set experiment type
    bnbExperiment = MultinomialNB()
    # train
    bnbExperiment.fit(makeVectorsResults["train"], readDataResults["classes"][:maxTrain])
    # test
    guesses = bnbExperiment.predict(makeVectorsResults["test"])
    confidences = bnbExperiment.predict_proba(makeVectorsResults["test"])
    guessesTrain = bnbExperiment.predict(makeVectorsResults["train"])
    # process results
    outFile = open(COMMAND+".out."+targetClass,"w")
    correct = 0
    guessTotal = 0
    goldTotal = 0
    for i in range(0,len(readDataResults["text"])-maxTrain):
        # show result per data line
        print >>outFile, "# %d: %s %s %0.3f" % (i+maxTrain,readDataResults["classes"][i+maxTrain],guesses[i],confidences[i][0])
        if guesses[i] == targetClass:
            guessTotal += 1
            if guesses[i] == readDataResults["classes"][i+maxTrain]: 
                correct += 1
        if readDataResults["classes"][i+maxTrain] == targetClass: 
            goldTotal += 1
    # compute correctness score for train data
    correctTrain = 0
    guessTotalTrain = 0
    goldTotalTrain = 0
    for i in range(0,maxTrain):
        if guessesTrain[i] == targetClass:
            guessTotalTrain += 1
            if guessesTrain[i] == readDataResults["classes"][i]: correctTrain += 1
        if readDataResults["classes"][i] == targetClass: 
            goldTotalTrain += 1
    # print result count
    precision = 0
    if guessTotal > 0: precision = 100*correct/guessTotal
    precisionTrain = 0
    if guessTotalTrain > 0: precisionTrain = 100*correctTrain/guessTotalTrain
    recall = 0
    if goldTotal > 0: recall = 100*correct/goldTotal
    recallTrain = 0
    if goldTotalTrain > 0: recallTrain = 100*correctTrain/goldTotalTrain
    print >>outFile, "Class: %s; Precision/Recall: %d%%/%d%%; Train: %d%%/%d%%" % (targetClass,precision,recall,precisionTrain,recallTrain)
    outFile.close()
 
