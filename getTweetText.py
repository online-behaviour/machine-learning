#!/usr/bin/python -W all
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
        # the json dictionary should contain a text and a language token: nl (Dutch)
        if "text" in jsonLine and "id_str" in jsonLine and \
            "user" in jsonLine and "screen_name" in jsonLine["user"] and \
            "lang" in jsonLine and jsonLine["lang"] == "nl":
            # print the text is csv format
            thisId = jsonLine["id_str"].encode("utf-8")
            screenName = jsonLine["user"]["screen_name"].encode("utf-8")
            text = jsonLine["text"].encode("utf-8")
            text = patternNewline.sub(" ",text)
            outFile.writerow([thisId,screenName,text])
    csvfile.close()
