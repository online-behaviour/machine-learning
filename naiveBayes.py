#!/usr/bin/python -W all
# naiveBayes.py: run naive bayes experiment
# usage: naiveBayes.py train-file
# 20170410 erikt(at)xs4all.nl

import csv
import re
import sys
from sklearn.naive_bayes import BernoulliNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB
import numpy

COMMAND = sys.argv[0]
TWEETCOLUMN = 4 # column number of tweet text in file dutch-2012.csv
CLASSCOLUMN = 9 # column number of tweeting behaviour (T#) in file dutch-2012.csv
if len(sys.argv) < 2: sys.exit("usage: "+COMMAND+" train-file\n")
trainFile = sys.argv[1]

# read the data from the file
text = []
classes = []
with open(trainFile,"rb") as csvfile:
    csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
    for row in csvreader: 
        text.append(row[TWEETCOLUMN])
        classes.append(row[CLASSCOLUMN])
    csvfile.close()
# throw away first data point: heading
text.pop(0)
classes.pop(0)

# tokenize the tweet text
tokenized = []
tokens = {}
tokenCount = 0
patternCharacter = re.compile("(.)")
patternPunctuation = re.compile("\W")
patternSpace = re.compile("\s")
for tweet in text:
    # convert tweet to lower case
    tweet = tweet.lower()
    # split text in characters
    tweetChars = patternCharacter.split(tweet)
    # build tokens from characters
    tweetTokens = []
    tweetTokenIndex = -1
    insideToken = False
    # examine each character in the tweet
    for c in tweetChars:
       # empty characters may be skipped
       if c == "":
           pass
       # white space signals the end of a token
       elif patternSpace.search(c):
           insideToken = False
       # punctuation characters should be seperate unextensible tokens
       elif patternPunctuation.search(c):
           tweetTokenIndex += 1
           tweetTokens.append(c)
           insideToken = False
       # characters [a-z0-9] should be appended to the current token
       elif insideToken:
           tweetTokens[tweetTokenIndex] = tweetTokens[tweetTokenIndex]+c
       # if we are not in a token, begin a new one
       else:
           tweetTokenIndex += 1
           tweetTokens.append(c)
           insideToken = True
    # add the tokens of this tweet to a global token list
    for t in tweetTokens:
        # if the token is unknown
        if not t in tokens:
            # add it to the token list with a unique id
            tokens[t] = tokenCount
            tokenCount += 1
    # add the tokens of this tweet to a token list
    tokenized.append(tweetTokens)

# make an empty vector
empty = []
for i in range(0,tokenCount): empty.append(0)
# make a vector list for the tweets
vectors = []
for i in range(0,len(tokenized)):
    vectors.append([])
    vectors[i] = list(empty)
    for token in tokenized[i]:
        if token not in tokens:
            sys.exit(COMMAND+": unknown token: "+token+"!\n")
        if tokens[token] >= len(vectors[i]):
            sys.exit(COMMAND+": index out of range: "+str(tokens[token])+" vs "+str(len(vectors))+"\n")
        vectors[i][tokens[token]] = 1
    vectors[i] = vectors[i][0:10000]
# now we are ready to run a machine learning experiment with vectors and classes

# perform naive bayes experiment
bnbExperiment = MultinomialNB() # GaussianNB() # BernoulliNB()
bnbExperiment.fit(vectors[0:1000], classes[0:1000])
correct = 0
for i in range(0,1000):
    guess = bnbExperiment.predict([vectors[i]])
    print "%d: %s %s" % (i,classes[i],guess[0])
    if guess[0] == classes[i]: correct += 1
# print result count
print "Total: %d; correct: %d" % (len(vectors),correct)

