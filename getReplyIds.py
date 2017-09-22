#!/usr/bin/python3 -W all
# getReplyIds.py: extract ids and reply-ids from tweets in json
# usage: getReplyIds.py < file
# 20170918 erikt(at)xs4all.nl

import csv
import json
import re
import sys

COMMAND = sys.argv.pop(0)
ID = "id"
REPLYTO = "in_reply_to_status_id"
SCREENNAME = "screen_name"
TEXT = "text"
USER = "user"

outFile = csv.writer(sys.stdout)
for line in sys.stdin:
    jsonLine = json.loads(line)
    if not ID in jsonLine or not REPLYTO in jsonLine or not TEXT in jsonLine or\
       not USER in jsonLine or not SCREENNAME in jsonLine[USER]:
        sys.exit(COMMAND+": unexpected line: "+line)
    pattern = re.compile("\n")
    jsonLine[TEXT] = pattern.sub(" ",jsonLine[TEXT])
    outFile.writerow([str(jsonLine[ID]),str(jsonLine[REPLYTO]),\
                      str(jsonLine[USER][SCREENNAME]),"PARTY",
                      str(jsonLine[TEXT])])
