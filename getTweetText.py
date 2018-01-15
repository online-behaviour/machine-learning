#!/usr/bin/python3 -W all
"""
    getTweetText.py: extract tweet text from json file
    usage: getTweetText.py < file
    20170418 erikt(at)xs4all.nl
"""

import csv
import json
import re
import sys

# command name for error messages
COMMAND = sys.argv[0]

patternNewline = re.compile("\n")
# open csv output
with sys.stdout as csvfile:
    outFile = csv.writer(csvfile,delimiter=",",quotechar='"')
    # repeat for each input line
    for line in sys.stdin:
        # convert the line to a json dictionary
        jsonLine = json.loads(line)
        # test for presence of required fields
        if not "id_str" in jsonLine: sys.exit(COMMAND+" missing id_str field")
        if not "text" in jsonLine: sys.exit(COMMAND+" missing text field")
        if not "user" in jsonLine: sys.exit(COMMAND+" missing user field")
        if not "screen_name" in jsonLine["user"]:
            sys.exit(COMMAND+" missing screen_name field")
        if not "in_reply_to_status_id_str" in jsonLine: 
            sys.exit(COMMAND+" missing in_reply_to_status_id_str field")
        # print the text in csv format
        thisId = jsonLine["id_str"]
        replyId = jsonLine["in_reply_to_status_id_str"]
        if replyId == None and "retweeted_status" in jsonLine and \
           "in_reply_to_status_id_str" in jsonLine["retweeted_status"]:
            replyId = jsonLine["retweeted_status"]["in_reply_to_status_id_str"]
        screenName = jsonLine["user"]["screen_name"]
        text = jsonLine["text"]
        text = patternNewline.sub(" ",text)
        outFile.writerow([thisId,replyId,screenName,text])
    csvfile.close()
