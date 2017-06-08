#!/usr/bin/python -W all
"""
    naiveBayes.py: run naive bayes experiment
    usage: naiveBayes.py -T train-file -t test-file [-e train-file-2] [-o offsett] [-c]
    note: input files are expected to contain csv (dutch-2012.csv, getTweetsText.out.1.text)
          option -c considers conversations
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

# constants definition
COMMAND = sys.argv.pop(0)
MINTOKENFREQ = 5     # minimum frequency of used tokens (rest is discarded)
NONE = -1 # non-existing column
TRAINCOLUMNTWEET = 4 # column tweet text in file dutch-2012.csv
TRAINCOLUMNCLASS = 9 # column tweeting behaviour (T3) in file dutch-2012.csv
TESTCOLUMNTWEET = 4 # column tweet text in test data file dutch-2012.csv
TESTCOLUMNCLASS = 9 # column tweeting behaviour (T3) in file dutch-2012.csv
TRAIN2COLUMNTWEET = 4 # column number of the tweet text in the extra training data
TRAIN2COLUMNCLASS = 0 # column number of the tweet class in the extra training data
OTHER = "O" # other value in binary experiment
IDCOLUMN = 0 # column with the id of the current tweet
PARENTCOLUMN = NONE # column of the id of the parent of the tweet if it is a retweet or reply (otherwise: None) (default: 5)

# getTargetClasses: read training data to determine target classes
def getTargetClasses(file,classColumn,fileHasHeading):
    targetClasses = []
    with open(file,"rb") as csvfile:
        csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
        lineNbr = 0
        for row in csvreader:
            lineNbr += 1
            # ignore first line if it is a heading
            if lineNbr == 1 and fileHasHeading: continue
            # add class to target class list
            if not row[classColumn] in targetClasses:
                targetClasses.append(row[classColumn])
        csvfile.close()
    return(targetClasses)    

# read the data from training or test file, with respect to certain target class
def readData(file,targetClass,tweetColumn,classColumn,idColumn,parentColumn,fileHasHeading):
    ids = []     # list with tweet ids
    text = []    # list with tweet texts
    classes = [] # list with tweet classes
    parentsIds = [] # list with ids of parent tweets
    with open(file,"rb") as csvfile:
        csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
        lineNbr = 0
        for row in csvreader:
            lineNbr += 1
            # ignore first line if it is a heading
            if lineNbr == 1 and fileHasHeading: continue
            # add tweet id to list
            ids.append(row[idColumn])
            # add tweet id to list
            parentsIds.append(row[parentColumn])
            # add tweet text to list
            text.append(row[tweetColumn])
            # add tweet class to list
            # add NONE if there is no class column
            if classColumn == NONE: classes.append(NONE)
            # add the targetClass whereever specified
            elif row[classColumn] == targetClass or targetClass == "": 
                classes.append(row[classColumn])
            # add OTHER for all other class values
            else: classes.append(OTHER)
        csvfile.close()
    # register the index value for each tweet id
    id2index = {}
    for i in range(0,len(ids)): id2index[ids[i]] = i
    # link parents by index
    parentsIndexes = []
    for i in range(0,len(parentsIds)): 
        if parentsIds[i] == "None": parentsIndexes.append("None")
        elif not parentsIds[i] in id2index: parentsIndexes.append("None")
        else: parentsIndexes.append(id2index[parentsIds[i]])
    # return results
    return({"text":text, "classes":classes, "ids":ids, "parents":parentsIndexes})

# tokenize the tweet text
def tokenize(text):
    tokenizedText = []   # list of lists of tokens per tweet
    patternEmail = re.compile("\S+@\S+")
    patternUserref = re.compile("@\S+")
    patternUrl = re.compile("http\S+")
    for i in range(0,len(text)):
        # convert tweet text to lower case 
        text[i] = text[i].lower()
        # collapse all mail addresses, urls and user references to one token
        text[i] = patternEmail.sub("MAIL",text[i])
        text[i] = patternUserref.sub("USER",text[i])
        text[i] = patternUrl.sub("HTTP",text[i])
        # tokenize the tweet
        tokenizedText.append(nltk.word_tokenize(unicode(text[i],"utf8")))
    return(tokenizedText)

# select tokens as features based on their frequencies
def selectFeatures(tokenizedText):
    # count tokens
    tokenCounts = {}
    for line in tokenizedText:
        for token in line:
            if token in tokenCounts: tokenCounts[token] += 1
            else: tokenCounts[token] = 1
    # select tokens based on frequency
    selectedTokens = {}
    for token in tokenCounts:
        if tokenCounts[token] >= MINTOKENFREQ:
            selectedTokens[token] = len(selectedTokens)
    # done
    return(selectedTokens)

# select tokens as features for vectors
def makeVectors(tokenizedText,selectedTokens,parentsIndexes,useConversations):
    # make a sparse data matrix for the training data
    rows = []    # row numbers of data point
    columns = [] # column numbers of data point
    data = []    # data values
    for i in range(0,len(tokenizedText)):
        index = i
        counts = {}
        while str(index) != "None":
            for token in tokenizedText[index]:
                if token in selectedTokens: 
                    if token in counts: counts[token] += 1
                    else: counts[token] = 1
            if not useConversations or parentsIndexes[index] == "None": break
            index = parentsIndexes[index]
        for token in counts:    
            # model alternatives: 1 or counts[token] (produce the same scores)
            data.append(1)
            rows.append(i)
            columns.append(selectedTokens[token])
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.html
    matrix = csr_matrix((data,(rows,columns)),shape=(len(tokenizedText),len(selectedTokens)))
    return(matrix) 

def main(argv):
    # train and test files
    testFile = ""
    trainFile = ""
    trainFile2 = ""
    # offset counter for line numbers in output
    offset = 0
    # conversation flag
    useConversations = False
    # usage error message
    usage = "usage: "+COMMAND+" -T train-file -t test-file [-e extra-train-file] [-o offset]"
    # process command line arguments
    try: options = getopt.getopt(argv,"T:t:e:o:c",[])
    except: sys.exit(usage)
    for option in options[0]:
        if option[0] == "-T": trainFile = option[1]
        elif option[0] == "-t": testFile = option[1]
        elif option[0] == "-e": trainFile2 = option[1]
        elif option[0] == "-o": offset = int(option[1])
        elif option[0] == "-c": useConversations = True
    if testFile == "" or trainFile == "": sys.exit(usage)
    # get target classes from training data file
    targetClasses = getTargetClasses(trainFile,TRAINCOLUMNCLASS,False)
    # perform a binary experiment (1 vs rest) for each target class
    for targetClass in sorted(targetClasses):
        # read the data from the training and test file
        readDataTrain = readData(trainFile,targetClass,TRAINCOLUMNTWEET,TRAINCOLUMNCLASS,IDCOLUMN,PARENTCOLUMN,False)
        readDataTest = readData(testFile,targetClass,TESTCOLUMNTWEET,TESTCOLUMNCLASS,IDCOLUMN,PARENTCOLUMN,False)
        if trainFile2 != "":
            readDataTrain2 = readData(trainFile2,targetClass,TRAIN2COLUMNTWEET,TRAIN2COLUMNCLASS,IDCOLUMN,PARENTCOLUMN,False)
            readDataTrain["text"].extend(readDataTrain2["text"])
            readDataTrain["classes"].extend(readDataTrain2["classes"])
            readDataTrain["parents"].extend(readDataTrain2["parents"])
        # tokenize the text
        trainTokenized = tokenize(readDataTrain["text"])
        testTokenized = tokenize(readDataTest["text"])
        # select tokens from the training data as features
        selectedTokens = selectFeatures(trainTokenized)
        # convert the text to a sparse number matrix
        trainMatrix = makeVectors(trainTokenized,selectedTokens,readDataTrain["parents"],useConversations)
        testMatrix = makeVectors(testTokenized,selectedTokens,readDataTest["parents"],useConversations)
        # perform naive bayes experiment
        # first: set experiment type
        # alternatives: MultinomialNB(50.5) GaussianNB(-) BernoulliNB(49.7)
        bnbExperiment = MultinomialNB()
        # train
        bnbExperiment.fit(trainMatrix,readDataTrain["classes"])
        # test
        confidences = bnbExperiment.predict_proba(testMatrix)
        # process results
        outFile = open(testFile+".out."+targetClass,"w")
        correct = 0
        guessTotal = 0
        goldTotal = 0
        # show result per data line
        for i in range(0,len(testTokenized)):
            print >>outFile, "# %d: %s %s %0.3f" % (i+offset,readDataTest["classes"][i],targetClass,confidences[i][0])
        outFile.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
