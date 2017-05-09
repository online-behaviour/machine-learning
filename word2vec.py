#!/usr/bin/python -W all
"""
    word2vec.py: process tweets with word2vec vectors
    usage: word2vec.py [-m model-file] -w word-vector-file -T train-file -t test-file
    note: optional model file is a text file from which the word vector file is built
    20170504 erikt(at)xs4all.nl
"""

# import modules & set up logging
import gensim
import getopt
import logging
import numpy
import naiveBayes
import os.path
import sys
from scipy.sparse import csr_matrix
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
from sklearn import svm

COMMAND = "word2vec.py"
MAXVECTOR = 200
TWEETCOLUMN = 4
CLASSCOLUMN = 9
HASHEADING = False
MINCOUNT = 5
USAGE = "usage: "+COMMAND+" [-m model-file] -w word-vector-file -T train-file -t test-file\n"

# check for command line options
trainFile = ""
testFile = ""
wordvectorFile = ""
modelFile = ""
try: options = getopt.getopt(sys.argv,"T:t:w:m:",[])
except: sys.exit(USAGE)
for option in options[0]:
    if option[0] == "-T": trainFile = option[1]
    elif option[0] == "-t": testFile = option[1]
    elif option[0] == "-w": wordvectorFile = option[1]
    elif option[0] == "-m": modelFile = option[1]
if trainFile == "" or testFile == "" or wordvectorFile == "":
    print trainFile
    sys.exit(USAGE)

# create data matrix; no sparse version needed
def makeVectors(tokenizeResults,wordvecModel):
    tweetVectors = numpy.zeros((len(tokenizeResults),MAXVECTOR),dtype=numpy.float64)
    # process all tweets
    for i in range(0,len(tokenizeResults)):
        if i == 1000*(int(i/1000)): print i # debugging: show process
        # process all tokens in this tweet
        for token in tokenizeResults[i]:
            # if the token is present in the word vector model
            if token in wordvecModel:
                # add (+) the word vector of this token to the tweet vector
                tweetVectors[i] += wordvecModel[token]
        # the result: a tweet vector which is the average of its token vectors
    return(tweetVectors)

def saveMatrix(matrix,fileName):
   try: outFile = open(fileName,"w")
   except: sys.exit(COMMAND+": cannot write to file "+fileName)
   for row in matrix:
       outLine = ""
       for i in range(0,len(row)):
           if i > 0:  outLine += ","
           outLine += str(row[i])
       print >>outFile,outLine
   outFile.close()

def makeBinary(vector):
    outVector = []
    for e in vector:
        if e == naiveBayes.OTHER: outVector.append(0)
        else: outVector.append(1)
    return(outVector)

# get target classes from training data file
targetClasses = naiveBayes.getTargetClasses(trainFile,CLASSCOLUMN,HASHEADING)
if len(targetClasses) == 0: sys.exit(COMMAND+": cannot find target classes\n")

# if required: train the word vector model and save it to file
if modelFile != "":
    readDataResults = naiveBayes.readData(modelFile,targetClasses[0],TWEETCOLUMN,CLASSCOLUMN,HASHEADING)
    tokenizeResults = naiveBayes.tokenize(readDataResults["text"])
    wordvecModel = gensim.models.Word2Vec(tokenizeResults, min_count=MINCOUNT, size=MAXVECTOR)
    wordvecModel.save(wordvectorFile)

# load the word vector model from file
wordvecModel = gensim.models.Word2Vec.load(wordvectorFile)

# load the test data, tokenize it and make wordvec tweet vectors
vectorFile = testFile+".wordvec"
if os.path.exists(vectorFile):
    # read vector file
    try: inFile = open(vectorFile,"r")
    except: sys.exit(COMMAND+": cannot read file "+vectorFile+"\n")
    makeVectorsResultsTest = []
    for line in inFile:
         line = line.rstrip()
         fields = line.split(",")
         if len(makeVectorsResultsTest) == 0:
             makeVectorsResultsTest = numpy.array([fields])
         else:
             makeVectorsResultsTest = numpy.append(makeVectorsResultsTest,[fields],0)
else:
    readDataResults = naiveBayes.readData(testFile,targetClasses[0],TWEETCOLUMN,CLASSCOLUMN,HASHEADING)
    tokenizeResults = naiveBayes.tokenize(readDataResults["text"])
    makeVectorsResultsTest = makeVectors(tokenizeResults,wordvecModel)
    saveMatrix(makeVectorsResultsTest,testFile+".wordvec")

# load the training data, tokenize it and make wordvec tweet vectors
vectorFile = trainFile+".wordvec"
if os.path.exists(vectorFile):
    # read vector file
    try: inFile = open(vectorFile,"r")
    except: sys.exit(COMMAND+": cannot read file "+vectorFile+"\n")
    makeVectorsResultsTrain = []
    for line in inFile:
         line = line.rstrip()
         fields = line.split(",")
         if len(makeVectorsResultsTrain) == 0:
             makeVectorsResultsTrain = numpy.array([fields])
         else:
             makeVectorsResultsTrain = numpy.append(makeVectorsResultsTrain,[fields],0)
else:
    readDataResults = naiveBayes.readData(trainFile,targetClasses[0],TWEETCOLUMN,CLASSCOLUMN,HASHEADING)
    tokenizeResults = naiveBayes.tokenize(readDataResults["text"])
    makeVectorsResultsTrain = makeVectors(tokenizeResults,wordvecModel)
    saveMatrix(makeVectorsResultsTrain,trainFile+".wordvec")

# run naive bayes experiments
for targetClass in ["4","9","13"]: # targetClasses:
    # read the training and test file again to get the right class distribution for this target class
    readDataResultsTrain = naiveBayes.readData(trainFile,targetClass,TWEETCOLUMN,CLASSCOLUMN,HASHEADING)
    readDataResultsTest = naiveBayes.readData(testFile,targetClass,TWEETCOLUMN,CLASSCOLUMN,HASHEADING)
    # perform naive bayes experiment
    # first: set experiment type
    # alternatives: MultinomialNB(50.5) GaussianNB(-) BernoulliNB(49.7)
    #bnbExperiment = BernoulliNB() # GaussianNB() # MultinomialNB()
    # train
    #bnbExperiment.fit(makeVectorsResultsTrain,readDataResultsTrain["classes"])
    # test
    #confidences = bnbExperiment.predict_proba(makeVectorsResultsTest)
    # perform svm experiment
    clf = svm.SVC(decision_function_shape='ovo')
    binTrainClasses = makeBinary(readDataResultsTrain["classes"])
    clf.fit(makeVectorsResultsTrain,binTrainClasses)
    outFile = open(testFile+".out."+targetClass,"w")
    for i in range(0,len(makeVectorsResultsTest)):
        # result = naiveBayes.OTHER
        # if (1 == clf.predict([makeVectorsResultsTest[i]])[0]): result = targetClass
        score = clf.decision_function([makeVectorsResultsTest[i]])[0]
        print >>outFile, "# %d: %s %0.3f" % (i,readDataResultsTest["classes"][i],score)
    outFile.close()

