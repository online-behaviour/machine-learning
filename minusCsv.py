#!/usr/bin/python -W all
"""
minusCsv.py: remove rows from a csv file based on values in a second file
usage: minusCsv.py -k column -F file2 -K column < file1
notes: removes rows with key values mentioned in file2 from file1
       when values in key columns k and K match
20170608 erikt(at)xs4all.nl
"""

import csv
import getopt
import re
import sys

# definition constants
COMMAND = sys.argv.pop(0)
NONE = -1
USAGE = COMMAND+": -k column -F file2 -K column < file1"
# definition variables
file1keyColumn = NONE
file2name = ""
file2keyColumn = NONE

def readCsv(fileName,keyColumn):
    data = {}
    with open(fileName,"rb") as csvfile:
        csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
        for row in csvreader:
            if len(row) < keyColumn:
                sys.exit(COMMAND+": unexpected line in file "+fileName+": "+(",".join(row))+"\n")
            # store key-value pair; do nothing special for heading
            data[row[keyColumn-1]] = True
        csvfile.close()
    return(data)

def main(argv):
    # process command line arguments
    try: options = getopt.getopt(argv,"k:F:K:",[])
    except: sys.exit(USAGE)
    for option in options[0]:
        if   option[0] == "-k": file1keyColumn = int(option[1])
        elif option[0] == "-F": file2name = option[1]
        elif option[0] == "-K": file2keyColumn= int(option[1])
    if file1keyColumn < 0 or file2name == "" or file2keyColumn < 0: sys.exit(USAGE)
    # read csv data from file 2, return as dictionary: file2[key] = True
    file2 = readCsv(file2name,file2keyColumn);
    # process csv data from stdin (file1)
    csvreader = csv.reader(sys.stdin,delimiter=',',quotechar='"')
    csvwriter = csv.writer(sys.stdout,delimiter=',',quotechar='"')
    for row in csvreader:
        # check if expected columns are present
        if len(row) < file1keyColumn:
            sys.exit(COMMAND+": unexpected line in stdin: "+(','.join(row))+"\n")
        if not row[file1keyColumn-1] in file2:
            csvwriter.writerow(row)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
