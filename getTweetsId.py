#!/usr/bin/python
"""
getTweetsId.py: get tweets from Twitter by tweet ids
usage: ./getTweets < file
20170711 erikt(at)xs4all.nl
"""

import json
import operator
import re
import sys
import time
# import twitter library: https://github.com/sixohsix/twitter
# /usr/local/lib/python2.7/dist-packages/twitter-1.17.1-py2.7.egg
from twitter import *
# put your authentication keys for Twitter in the local file definitions.py
# like: token = "..."
import definitions

# constants
COMMAND = sys.argv[0]
# stop the program after this many warnings
MAXWARNINGS =  50
# maximum count for remaining Twitter requests
MAXREMAINING = 900
# group of Twitter REST api used
APIGROUP = "statuses"
# Twitter REST api used
API = "/"+APIGROUP+"/lookup"
# maximum number of tweets we can retrieve from Twitter with one call
MAXTWEETS = 100

def readIds():
    ids = []
    for line in sys.stdin:
        line = line.rstrip()
        fields = line.split()
        for field in fields:
            if field != "": ids.append(field)
    return(ids)

def checkRemaining(t,apigroup,api):
    # check the rate limit; if 0 then wait
    rates = t.application.rate_limit_status(resources = apigroup)
    remaining = rates['resources'][apigroup][api]['remaining']
    # check if there are remaining calls
    while remaining < 1:
        # if not: wait one minute
        time.sleep(60)
        # fetch the value of the remaining count from Twitter
        rates = t.application.rate_limit_status(resources = apigroup)
        remaining = rates['resources'][apigroup][api]['remaining']
    return(remaining)

def main():
    # Twitter autnetication keys
    token = definitions.token
    token_secret = definitions.token_secret
    consumer_key =  definitions.consumer_key
    consumer_secret = definitions.consumer_secret
    # warning count
    nbrOfWarnings = 0

    # authenticate
    t = Twitter(auth=OAuth(token, token_secret, consumer_key, consumer_secret))
    # check if we can access the api at Twitter, wait if necessary
    remaining = checkRemaining(t,APIGROUP,API) 
    # read tweet ids from stdin
    ids = readIds()
    # repeat for every user
    while len(ids) > 0:
        # set number of retrieved tweets: MAXTWEETS is default value
        batch = ids[0:MAXTWEETS]
        ids = ids[MAXTWEETS:]
        batchString = ""
        for b in batch:
            if batchString != "": batchString += ","
            batchString += b
        results = []
        try:
            results = t.statuses.lookup(id=batchString)
            #results = t.statuses.lookup(id = batchString)
        except TwitterHTTPError as e:
            # if there is an error: report this
            sys.stderr.write("error: "+str(e))
            nbrOfWarnings += 1
        # stop if there were too many errors
        if nbrOfWarnings >= MAXWARNINGS:
            sys.exit(COMMAND+": too many warnings: "+nbrOfWarnings+"\n")
        # check if we have some results
        # if not "statuses" in results:
        #    sys.exit(COMMAND+": incomplete results: aborting!\n")
        # process results
        for tweet in results:
            # print the tweet in json format
            print json.dumps(tweet,sort_keys=True)
        # decrement remaining counter
        remaining -= 1
        # check if we can still access the api
        if remaining < 1: remaining = checkRemaining(t,APIGROUP,API)

# default action on script call: run main function
if __name__ == "__main__":
    sys.exit(main())
