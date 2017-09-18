#!/usr/bin/python3 -W all
# getReplyIds.py: extract ids and reply-ids from tweets in json
# usage: getReplyIds.py < file
# 20170918 erikt(at)xs4all.nl

import json
import sys

COMMAND = sys.argv.pop()
ID = "id"
REPLYTO = "in_reply_to_status_id"

for line in sys.stdin:
    jsonLine = json.loads(line)
    if not ID in jsonLine or not REPLYTO in jsonLine:
        sys.exit(COMMAND+": unexpected line: "+line)
    print(str(jsonLine[ID])+" "+str(jsonLine[REPLYTO]))
