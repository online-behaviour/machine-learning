#!/usr/bin/python
"""
getTweetsUser.py: get recent tweets from Twitter of certain users
usage: ./getTweets user1 [user2 ...] > file
20170418 erikt(at)xs4all.nl
"""

import json
import operator
import re
import sys
import time
# import twitter library: https://github.com/sixohsix/twitter
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
API = "/"+APIGROUP+"/user_timeline"
# maximum number of tweets we can retrieve from Twitter with one call
MAXTWEETS = 200
# if the query is too long, Twitter will fail with error missing url parameter
users = sys.argv
# remove the program name from the users list
users.pop(0)

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
    # repeat for every user
    for user in users:
        # set last tweet that was retrieved
        lastTweetId = -1
        # set number of retrieved tweets: MAXTWEETS is default value
        nbrOfTweets = MAXTWEETS
        # get all available tweets
        while nbrOfTweets == MAXTWEETS:
            try:
                if lastTweetId > 0:
                    results = t.statuses.user_timeline(screen_name = user, count = 200, max_id =  lastTweetId)
                else:
                    results = t.statuses.user_timeline(screen_name = user, count = 200)
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
            # check how many tweets have been retrieved (compare with MAXTWEETS later)
            nbrOfTweets = len(results)
            # get id of final tweet that was retrieved
            if len(results) <= 0: lastTweetId = -1
            else: lastTweetId = int(results[-1]["id"])-1
            # decrement remaining counter
            remaining -= 1
            # check if we can still access the api
            if remaining < 1: remaining = checkRemaining(t,APIGROUP,API)

# default action on script call: run main function
if __name__ == "__main__":
    sys.exit(main())
