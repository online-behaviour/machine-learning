#!/usr/bin/python -W all
"""
combineCsv.py: adapt values in a csv file based on values in a second file
usage: combineCsv.py [-c] -k column -v column -F file2 -K column -V column < file1
notes: changes values in column v of file1 to value in column V of file2
       when values in key columns k and K match
       option -c will invoke printing only changed rows (default: print all)
20170608 erikt(at)xs4all.nl
"""

import csv
import getopt
import re
import sys

# definition constants
COMMAND = sys.argv.pop(0)
NONE = -1
USAGE = COMMAND+": -k column -v column -F file2 -K column -V column < file1"
# definition variables
file1keyColumn = NONE
file1valueColumn = NONE
file2name = ""
file2keyColumn = NONE
file2valueColumn = NONE
changedSelect = False

def readCsv(fileName,keyColumn,valueColumn):
    data = {}
    with open(fileName,"rb") as csvfile:
        csvreader = csv.reader(csvfile,delimiter=',',quotechar='"')
        for row in csvreader:
            if len(row) < keyColumn or len(row) < valueColumn:
                sys.exit(COMMAND+": unexpected line in file "+fileName+": "+(",".join(row))+"\n")
            # store key-value pair; do nothing special for heading
            data[row[keyColumn-1]] = row[valueColumn-1]
        csvfile.close()
    return(data)

def main(argv):
    global changedSelect,file1keyColumn,file1valueColumn,file2name,file2keyColumn,file2valueColumn

    # process command line arguments
    try: options = getopt.getopt(argv,"ck:v:F:K:V:",[])
    except: sys.exit(USAGE)
    for option in options[0]:
        if   option[0] == "-k": file1keyColumn = int(option[1])
        elif option[0] == "-v": file1valueColumn = int(option[1])
        elif option[0] == "-F": file2name = option[1]
        elif option[0] == "-K": file2keyColumn= int(option[1])
        elif option[0] == "-V": file2valueColumn = int(option[1])
        elif option[0] == "-c": changedSelect = True
    if file1keyColumn == NONE or file1valueColumn == NONE or \
       file2name == "" or file2keyColumn == NONE or file2valueColumn == NONE: sys.exit(USAGE)
    # read csv data from file 2, return as dictionary: file2[key] = value
    file2 = readCsv(file2name,file2keyColumn,file2valueColumn);
    # process csv data from stdin (file1)
    csvreader = csv.reader(sys.stdin,delimiter=',',quotechar='"')
    csvwriter = csv.writer(sys.stdout,delimiter=',',quotechar='"')
    for row in csvreader:
        # check if expected columns are present
        if len(row) < file1keyColumn or len(row) < file1valueColumn:
            sys.exit(COMMAND+": unexpected line in stdin: "+(','.join(row))+"\n")
        if row[file1keyColumn-1] in file2:
            row[file1valueColumn-1] = file2[row[file1keyColumn-1]]
            # print this changed row if changedSelect flag is set
            if changedSelect: csvwriter.writerow(row)
        # print every row if changedSelect flag is not set
        if not changedSelect: csvwriter.writerow(row)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
