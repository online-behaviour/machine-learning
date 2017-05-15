#!/usr/bin/python -W all
"""
    naiveBayes.py: run naive bayes experiment
    usage: naiveBayes.py -T train-file -t test-file [-e train-file-2] [-o offsett]
    note: input files are expected to contain csv (dutch-2012.csv, getTweetsText.out.1.text)
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
def readData(file,targetClass,tweetColumn,classColumn,fileHasHeading):
    text = [] # list with tweet texts
    classes = [] # list with tweet classes
    with open(file,"rb") as csvfile:
        csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
        lineNbr = 0
        for row in csvreader:
            lineNbr += 1
            # ignore first line if it is a heading
            if lineNbr == 1 and fileHasHeading: continue
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
    # return results
    return({"text":text, "classes":classes})

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
def makeVectors(tokenizedText,selectedTokens):
    # make a sparse data matrix for the training data
    rows = []    # row numbers of data point
    columns = [] # column numbers of data point
    data = []    # data values
    for i in range(0,len(tokenizedText)):
        counts = {}
        for token in tokenizedText[i]:
            if token in selectedTokens: 
                if token in counts: counts[token] += 1
                else: counts[token] = 1
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
    # usage error message
    usage = "usage: "+COMMAND+" -T train-file -t test-file [-e extra-train-file] [-o offset]"
    # process command line arguments
    try: options = getopt.getopt(argv,"T:t:e:o:",[])
    except: sys.exit(usage)
    for option in options[0]:
        if option[0] == "-T": trainFile = option[1]
        elif option[0] == "-t": testFile = option[1]
        elif option[0] == "-e": trainFile2 = option[1]
        elif option[0] == "-o": offset = int(option[1])
    if testFile == "" or trainFile == "": sys.exit(usage)
    # get target classes from training data file
    targetClasses = getTargetClasses(trainFile,TRAINCOLUMNCLASS,False)
    # perform a binary experiment (1 vs rest) for each target class
    for targetClass in sorted(targetClasses):
        # read the data from the training and test file
        readDataTrain = readData(trainFile,targetClass,TRAINCOLUMNTWEET,TRAINCOLUMNCLASS,False)
        readDataTest = readData(testFile,targetClass,TESTCOLUMNTWEET,TESTCOLUMNCLASS,False)
        if trainFile2 != "":
            readDataTrain2 = readData(trainFile2,targetClass,TRAIN2COLUMNTWEET,TRAIN2COLUMNCLASS,False)
            readDataTrain["text"].extend(readDataTrain2["text"])
            readDataTrain["classes"].extend(readDataTrain2["classes"])
        # tokenize the text
        trainTokenized = tokenize(readDataTrain["text"])
        testTokenized = tokenize(readDataTest["text"])
        # select tokens from the training data as features
        selectedTokens = selectFeatures(trainTokenized)
        # convert the text to a sparse number matrix
        trainMatrix = makeVectors(trainTokenized,selectedTokens)
        testMatrix = makeVectors(testTokenized,selectedTokens)
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
