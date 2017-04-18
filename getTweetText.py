#!/usr/bin/python -W all
"""
    getTweetText.py: extract tweet text from json file
    usage: getTweetText.py < file
    20170418 erikt(at)xs4all.nl
"""

import json
import sys

# command name for error messages
COMMAND = sys.argv[0]

# repeat for each input line
for line in sys.stdin:
    # convert the line to a json dictionary
    jsonLine = json.loads(line)
    # the json dictionary should contain a text and a language token: nl (Dutch)
    if "text" in jsonLine and "id_str" in jsonLine and \
        "user" in jsonLine and "screen_name" in jsonLine["user"] and \
        "lang" in jsonLine and jsonLine["lang"] == "nl":
        # print the text
        print "%s %s %s" % \
           (jsonLine["id_str"].encode("utf-8"),
            jsonLine["user"]["screen_name"].encode("utf-8"),
            jsonLine["text"].encode("utf-8"))

