#!/usr/bin/python -W all
"""
    word2vec.py: process tweets with word2vec vectors
    usage: word2vec.py -T train-file -t test-file
    20170504 erikt(at)xs4all.nl
"""

# import modules & set up logging
import gensim, logging
import naiveBayes
#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

MAXVECTOR = 10

# create data matrix; no sparse version needed
def makeVectors(tokenizeResults,wordvecModel):
    matrix = []
    for i in range(0,len(tokenizeResults)):
        print i
        matrix.append([])
        nbrOfTokens = 0
        for token in tokenizeResults[i]:
            if token in wordvecModel:
                nbrOfTokens += 1
                for j in range(0,MAXVECTOR):
                    if j in matrix[i]: matrix[i][j] += wordvecModel[token][j]
                    else: matrix[i].append(wordvecModel[token][j])
        for j in range(0,MAXVECTOR):
            if j in matrix[i]: matrix[i][j] /= nbrOfTokens
            else: matrix[i][j] = 0.0
    return(matrix)

# train the word vector model and save it to file
# readDataResults = naiveBayes.readData("dutch-2012.train.csv","1",4,9,False)
# tokenizeResults = naiveBayes.tokenize(readDataResults["text"])
# wordvecModel = gensim.models.Word2Vec(tokenizeResults, min_count=5, size=MAXVECTOR)
# wordvecModel.save ("word2vec.train.model")

# load the word vector model from file
wordvecModel = gensim.models.Word2Vec.load("word2vec.train.model")

# repeat the next lines for the 13 target classes

# load the training data, tokenize it and make wordvec tweet vectors
readDataResults = naiveBayes.readData("dutch-2012.train.csv","1",4,9,False)
tokenizeResults = naiveBayes.tokenize(readDataResults["text"])
makeVectorsResultsTrain = makeVectors(tokenizeResults,wordvecModel)
# save the data to file to avoid having to compute it again

# load the test data, tokenize it and make wordvec tweet vectors
readDataResults = naiveBayes.readData("dutch-2012.test.csv","1",4,9,False)
tokenizeResults = naiveBayes.tokenize(readDataResults["text"])
makeVectorsResultsTest = makeVectors(tokenizeResults,wordvecModel)

# run naive bayes experiment


