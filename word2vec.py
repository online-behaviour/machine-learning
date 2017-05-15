#!/usr/bin/python -W all
"""
    word2vec.py: process tweets with word2vec vectors
    usage: word2vec.py [-x] [-m model-file [-l word-vector-length]] -w word-vector-file -T train-file -t test-file
    notes: 
    - optional model file is a text file from which the word vector file is built
    - option x writes tokenized sentences to stdout
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

# constants
COMMAND = "word2vec.py"
TWEETCOLUMN = 4
CLASSCOLUMN = 9
HASHEADING = False
MINCOUNT = 5
USAGE = "usage: "+COMMAND+" [-m model-file] -w word-vector-file -T train-file -t test-file\n"

# input file names
trainFile = ""
testFile = ""
wordvectorFile = ""
modelFile = ""
# length of word vectors
maxVector = 200
# exporting tokenized sentences
exportTokens = False

# check for command line options
def checkOptions():
    global trainFile
    global testFile
    global wordvectorFile
    global modelFile
    global maxVector
    global exportTokens

    try: options = getopt.getopt(sys.argv,"T:t:w:m:l:x",[])
    except: sys.exit(USAGE)
    for option in options[0]:
        if option[0] == "-T": trainFile = option[1]
        elif option[0] == "-t": testFile = option[1]
        elif option[0] == "-w": wordvectorFile = option[1]
        elif option[0] == "-m": modelFile = option[1]
        elif option[0] == "-l": maxVector = int(option[1])
        elif option[0] == "-x": exportTokens = True
    if trainFile == "" or testFile == "" or wordvectorFile == "":
        print trainFile
        sys.exit(USAGE)

# create data matrix (no sparse version needed)
def makeVectors(tokenizeResults,wordvecModel):
    tweetVectors = numpy.zeros((len(tokenizeResults),maxVector),dtype=numpy.float64)
    # process all tweets
    for i in range(0,len(tokenizeResults)):
        # process all tokens in this tweet
        for token in tokenizeResults[i]:
            # if the token is present in the word vector model
            if token in wordvecModel:
                # add (+) the word vector of this token to the tweet vector
                tweetVectors[i] += wordvecModel[token]
        # the result: a tweet vector which is the sum of its token vectors
    return(tweetVectors)

# change the class vector into a binary vector
def makeBinary(vector):
    outVector = []
    for e in vector:
        if e == naiveBayes.OTHER: outVector.append(0)
        else: outVector.append(1)
    return(outVector)

# main function starts here
checkOptions()

# get target classes from training data file
targetClasses = naiveBayes.getTargetClasses(trainFile,CLASSCOLUMN,HASHEADING)
if len(targetClasses) == 0: sys.exit(COMMAND+": cannot find target classes\n")

# if required: train the word vector model and save it to file
if modelFile != "":
    # read the model data
    readDataResults = naiveBayes.readData(modelFile,targetClasses[0],TWEETCOLUMN,CLASSCOLUMN,HASHEADING)
    # tokenize the model data
    tokenizeResults = naiveBayes.tokenize(readDataResults["text"])
    # build the word vectors (test sg=1,window=10)
    wordvecModel = gensim.models.Word2Vec(tokenizeResults, min_count=MINCOUNT, size=maxVector)
    # save the word vectors
    wordvecModel.save(wordvectorFile)

# load the word vector model from file
wordvecModel = gensim.models.Word2Vec.load(wordvectorFile)

# read training data, tokenize data, make vector matrix
readDataResults = naiveBayes.readData(trainFile,"",TWEETCOLUMN,CLASSCOLUMN,HASHEADING)
tokenizeResults = naiveBayes.tokenize(readDataResults["text"])
if exportTokens:
    for i in range(0,len(tokenizeResults)):
        sys.stdout.write("__label__"+readDataResults["classes"][i])
        for j in range(0,len(tokenizeResults[i])): 
            sys.stdout.write(" ")
            sys.stdout.write(unicode(tokenizeResults[i][j]).encode('utf8'))
        sys.stdout.write("\n")
    sys.exit()
makeVectorsResultsTrain = makeVectors(tokenizeResults,wordvecModel)
# the matrix can be saved to file and reloaded in next runs but this does not gain much time

# read test data, tokenize data, make vector matrix
readDataResults = naiveBayes.readData(testFile,"",TWEETCOLUMN,CLASSCOLUMN,HASHEADING)
tokenizeResults = naiveBayes.tokenize(readDataResults["text"])
makeVectorsResultsTest = makeVectors(tokenizeResults,wordvecModel)

# run binary svm experiments: one for each target class
for targetClass in targetClasses:
    # read the training and test file again to get the right class distribution for this target class
    readDataResultsTrain = naiveBayes.readData(trainFile,targetClass,TWEETCOLUMN,CLASSCOLUMN,HASHEADING)
    readDataResultsTest = naiveBayes.readData(testFile,targetClass,TWEETCOLUMN,CLASSCOLUMN,HASHEADING)
    # get binary version of train classes
    binTrainClasses = makeBinary(readDataResultsTrain["classes"])
    # perform svm experiment: http://scikit-learn.org/stable/modules/svm.html (1.4.1.1)
    clf = svm.SVC(decision_function_shape='ovo')     # definition
    clf.fit(makeVectorsResultsTrain,binTrainClasses) # training
    outFile = open(testFile+".out."+targetClass,"w") # output file for test results
    for i in range(0,len(makeVectorsResultsTest)):
        score = clf.decision_function([makeVectorsResultsTest[i]])[0] # process one test item
        print >>outFile, "# %d: %s %0.3f" % (i,readDataResultsTest["classes"][i],score)
    outFile.close()

