#!/usr/bin/python -W all
"""
    naiveBayes.py: run naive bayes experiment
    usage: naiveBayes.py train-file [test-file [train-file2]]
    note: input files are expected to contain csv (dutch-2012.csv, getTweetsText.out.1.text)
    warning: do not uses both a filled test-file and filled train-file2
    20170410 erikt(at)xs4all.nl
"""

import csv
import getopt
import nltk
import numpy
import re
import sys
from scipy.sparse import csr_matrix
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB

COMMAND = sys.argv.pop(0)
MINFREQ = 5     # minimum frequency of used tokens (rest is discarded)
TWEETCOLUMN = 4 # column number of tweet text in file dutch-2012.csv
CLASSCOLUMN = 9 # column number of tweeting behaviour (T3) in file dutch-2012.csv
UNSEENCOLUMN = 2 # column with tweet test in test data file getTweetsUser.out.1.text.gz
NONE = -1 # non-existing column
TRAIN2TEXT = 4 # column number of the tweet text in the extra training data
TRAIN2CLASS = 0 # column number of the tweet class in the extra training data
TRAINPART = 0.9 # percentage of the data used as training data; rest is test
USELAST = False # use the last part of the data as test (True) or the first (False)
OTHER = "O" # other value in binary experiment

# get the name of the data file from the command line
if len(sys.argv) < 1: sys.exit("usage: "+COMMAND+" train-file [unseen-file]\n")
trainFile = sys.argv.pop(0)
targetClasses = ["1","2","3","4","5","6","7","8","9","10","11","12","13"]
# file with unseen data that needs to be classified 
unseenFile = ""
if len(sys.argv) > 0:
    unseenFile = sys.argv.pop(0)
# file with additional training data
trainFile2 = ""
if len(sys.argv) > 0:
    trainFile2 = sys.argv.pop(0)

# read the data from the training file
def readData(file,targetClass,tweetColumn,classColumn,hasHeading):
    text = []
    classes = []
    with open(file,"rb") as csvfile:
        csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
        for row in csvreader: 
            text.append(row[tweetColumn])
            if classColumn == NONE: classes.append(NONE)
            elif row[classColumn] == targetClass: classes.append(row[classColumn])
            else: classes.append(OTHER)
        csvfile.close()
    # throw away first data point: heading
    if (hasHeading):
        text.pop(0)
        classes.pop(0)
    # return results
    return({"text":text, "classes":classes})

# tokenize the tweet text
def tokenize(text,minTrain,maxTrain,minTrain2):
    tokenized = []   # list of lists of tokens per tweet
    tokenCounts = {} # dictionary with per-token counts in training data
    tokenList = []   # list of all tokens
    patternEmail = re.compile("\S+@\S+")
    patternUserref = re.compile("@\S+")
    patternUrl = re.compile("http\S+")
    for i in range(0,len(text)):
        # print "TOKENIZE: %s" % (text[i])
        # convert tweet text to lower case 
        text[i] = text[i].lower()
        # collapse all mail addresses, urls and user references to one token
        text[i] = patternEmail.sub("MAIL",text[i])
        text[i] = patternUserref.sub("USER",text[i])
        text[i] = patternUrl.sub("HTTP",text[i])
        tokenized.append(nltk.word_tokenize(unicode(text[i],"utf8")))
        for token in tokenized[-1]:
            if token in tokenCounts: tokenCounts[token] += 1
            else: 
               tokenCounts[token] = 1
               tokenList.append(token)
    return({"tokenized":tokenized,"tokenList":tokenList,"tokenCounts":tokenCounts})

# select tokens as features for vectors
def makeVectors(tokenizeResults,minTrain,maxTrain,minTest,maxTest,minUnseen,minTrain2):
    # select the most frequent tokens as features
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
    for i in range(minTrain,maxTrain):
        for token in tokenizeResults["tokenized"][i]:
            if token in selectedTokens:
                data.append(1) # count for this token: use 1
                rows.append(i-minTrain)
                columns.append(selectedIds[token])
    # if there is an additional second training data set: add it
    trainSize = maxTrain-minTrain
    if minTrain2 != NONE:
        trainSize += len(tokenizeResults["tokenized"])-minTrain2
        for i in range(minTrain2,len(tokenizeResults["tokenized"])):
            for token in tokenizeResults["tokenized"][i]:
                if token in selectedTokens:
                    data.append(1) # count for this token: use 1
                    rows.append(i-minTrain2+maxTrain-minTrain)
                    columns.append(selectedIds[token])
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.html
    train = csr_matrix((data,(rows,columns)),shape=(trainSize,len(selectedTokens)))
    # make a sparse data matrix for the test data
    rows = []
    columns = []
    data = []
    for i in range(minTest,maxTest):
        for token in tokenizeResults["tokenized"][i]:
            if token in selectedTokens:
                data.append(1) # count for this token: use 1
                rows.append(i-minTest)
                columns.append(selectedIds[token])
    test = csr_matrix((data,(rows,columns)),shape=(maxTest-minTest,len(selectedTokens)))
    # make a sparse data matrix for the unseen data
    rows = []
    columns = []
    data = []
    if minUnseen == NONE:
        return({"train":train,"test":test}) 
    else:
        for i in range(minUnseen,len(tokenizeResults["tokenized"])):
            for token in tokenizeResults["tokenized"][i]:
                if token in selectedTokens:
                    data.append(1) # count for this token: use 1
                    rows.append(i-minUnseen)
                    columns.append(selectedIds[token])
        unseen = csr_matrix((data,(rows,columns)),shape=(len(tokenizeResults["tokenized"])-minUnseen,len(selectedTokens)))
        return({"train":train,"test":test,"unseen":unseen}) 

for targetClass in targetClasses:
    # read the data from the training file
    readDataResults = readData(trainFile,targetClass,TWEETCOLUMN,CLASSCOLUMN,True)
    # use 90% of the data as train; 10% as test
    # note: the data is assumed to be sorted by time
    if USELAST:
       minTrain = 0
       maxTrain = int(TRAINPART*len(readDataResults["text"]))
       minTest = maxTrain
       maxTest = len(readDataResults["text"])
    else:
       minTest = 0
       maxTest = int((1-TRAINPART)*len(readDataResults["text"]))
       minTrain = maxTest
       maxTrain = len(readDataResults["text"])
    unseenResults = {}
    minUnseen = NONE
    if unseenFile != "": 
        unseenResults = readData(unseenFile,targetClass,UNSEENCOLUMN,NONE,False)
        # if the unseen file is empty: no need to process the unseen data
        if not "text" in unseenResults or len(unseenResults["text"]) == 0:
            unseenFile = ""
    # add unseen text (if any) to data
    if "text" in unseenResults and "classes" in unseenResults:
        minUnseen = len(readDataResults["text"])
        readDataResults["text"].extend(unseenResults["text"])
        readDataResults["classes"].extend(unseenResults["classes"])
    train2Results = {}
    minTrain2 = NONE
    if trainFile2 != "":
        train2Results = readData(trainFile2,targetClass,TRAIN2TEXT,TRAIN2CLASS,False)
    if "text" in train2Results and "classes" in train2Results:
        minTrain2 = len(readDataResults["text"]) # cannot be combined with non-empty unseen data!
        readDataResults["text"].extend(train2Results["text"])
        readDataResults["classes"].extend(train2Results["classes"])

    # tokenize the text in the data
    tokenizeResults = tokenize(readDataResults["text"],minTrain,maxTrain,minTrain2)
    # convert the text to token vectors (make selection)
    makeVectorsResults = makeVectors(tokenizeResults,minTrain,maxTrain,minTest,maxTest,minUnseen,minTrain2)
    
    # perform naive bayes experiment
    # alternatives: MultinomialNB() GaussianNB() BernoulliNB()
    # first: set experiment type
    bnbExperiment = MultinomialNB()
    # train
    classes = readDataResults["classes"][minTrain:maxTrain]
    if minTrain2 != NONE: classes.extend(readDataResults["classes"][minTrain2:])
    bnbExperiment.fit(makeVectorsResults["train"],classes)
    # test
    guesses = bnbExperiment.predict(makeVectorsResults["test"])
    confidences = bnbExperiment.predict_proba(makeVectorsResults["test"])
    guessesTrain = bnbExperiment.predict(makeVectorsResults["train"])
    # process results
    outFile = open(COMMAND+".out."+targetClass,"w")
    correct = 0
    guessTotal = 0
    goldTotal = 0
    for i in range(0,maxTest-minTest):
        # show result per data line
        print >>outFile, "# %d: %s %s %0.3f" % (i+minTest,readDataResults["classes"][i+minTest],guesses[i],confidences[i][0])
        if guesses[i] == targetClass:
            guessTotal += 1
            if guesses[i] == readDataResults["classes"][i+minTest]: 
                correct += 1
        if readDataResults["classes"][i+minTest] == targetClass: 
            goldTotal += 1
    # compute correctness score for train data
    correctTrain = 0
    guessTotalTrain = 0
    goldTotalTrain = 0
    for i in range(0,maxTrain-minTrain):
        if guessesTrain[i] == targetClass:
            guessTotalTrain += 1
            if guessesTrain[i] == readDataResults["classes"][i+minTrain]: correctTrain += 1
        if readDataResults["classes"][i+minTrain] == targetClass: 
            goldTotalTrain += 1
    # print result count
    precision = 0.0
    if guessTotal > 0: precision = 100.0*float(correct)/float(guessTotal)
    precisionTrain = 0.0
    if guessTotalTrain > 0: precisionTrain = 100.0*float(correctTrain)/float(guessTotalTrain)
    recall = 0.0
    if goldTotal > 0: recall = 100.0*float(correct)/float(goldTotal)
    recallTrain = 0
    if goldTotalTrain > 0: recallTrain = 100.0*float(correctTrain)/float(goldTotalTrain)
    print >>outFile, "Class: %s; Precision/Recall: %0.1f%%/%0.1f%%; Train: %0.1f%%/%0.1f%%" % (targetClass,precision,recall,precisionTrain,recallTrain)
    outFile.close()
    # process unseen data
    if unseenFile != "":
        # classify unseen data
        guesses = bnbExperiment.predict(makeVectorsResults["unseen"])
        confidences = bnbExperiment.predict_proba(makeVectorsResults["unseen"])
        outFile = open(COMMAND+".unseen."+targetClass,"w")
        # print results
        for i in range(0,len(guesses)):
            # show result per data line
            print >>outFile, "# %d: %s %s %0.3f" % (i,readDataResults["classes"][i+minUnseen],guesses[i],confidences[i][0])
        outFile.close()

