#!/bin/bash
# run: run active learning experiment
# usage: run
# 20170829 erikt(at)xs4all.nl

COMMAND="$0"
REVERSE=""
BATCHSIZE1=5500
BATCHSIZE2=550
METHOD1="t"
TRAIN=dutch-2012.train-dev.txt.replyto
TEST=dutch-2012.dev.txt.replyto
VECTORS=vectors-train-dev.vec
TMPFILE=run.$$.$RANDOM
TMPTRAIN=$TMPFILE.train
TMPREST=$TMPFILE.rest
TMPPROBS=$TMPFILE.probs
TMPSTART=$TMPFILE.start
DIM=300
MINCOUNT=5
NBROFCLASSES=12
BINDIR=/home/cloud/projects/online-behaviour/machine-learning
SELECT=$BINDIR/active-select.py

function run-experiment {
   METHOD=$1
   cat $TRAIN > $TMPREST
   echo -e "\c" > $TMPTRAIN
   echo -e "\c" > $TMPPROBS
   for i in {1..11}
   do
      if [ $i == 1 ]; then BATCHSIZE=$BATCHSIZE1; else BATCHSIZE=$BATCHSIZE2; fi
      if [ $i -gt 1 -o "$METHOD$REVERSE" == $METHOD1 ]; then
         $SELECT -d $TMPREST -p $TMPPROBS -z $BATCHSIZE -a -$METHOD $REVERSE > $TMPFILE
         if [ ! -s $TMPFILE ]; then echo $0: $SELECT failed >&2; exit 1; fi
         if [ $i == 1 -a "$METHOD$REVERSE" == $METHOD1 ]; then cp $TMPFILE $TMPSTART; fi
      else
         if [ ! -f $TMPSTART ]; then echo $COMMAND: no start file>&2; fi
         cp $TMPSTART $TMPFILE
      fi
      head -$BATCHSIZE $TMPFILE >> $TMPTRAIN
      tail -n +$(($BATCHSIZE+1)) $TMPFILE > $TMPREST
      TRAINSIZE=`wc -l < $TMPTRAIN`
      if [ $i -gt 1 -o "$METHOD$REVERSE" == $METHOD1 ]; then
         ../fasttext supervised -input $TMPTRAIN -output $TMPFILE -dim $DIM \
            -pretrainedVectors $VECTORS -minCount $MINCOUNT >/dev/null 2>/dev/null
         if [ $i == 1 -a "$METHOD$REVERSE" == $METHOD1 ]; then cp $TMPFILE.bin $TMPSTART.bin; fi
      else
         if [ ! -f $TMPSTART.bin ]; then echo $COMMAND: no start model>&2; fi
         cp $TMPSTART.bin $TMPFILE.bin
      fi
      ../fasttext predict $TMPFILE.bin $TEST |\
         paste -d' ' -  $TEST | cut -d' ' -f1,2 | $BINDIR/eval.py | head -1 |\
         rev | sed 's/^ *//' | cut -d' ' -f1 | rev | sed 's/^/P@1\t/' |\
         sed "s/^/$METHOD$REVERSE $BATCHSIZE $TRAINSIZE /"
      if [ $METHOD != "r" -a $METHOD != "l" -a $METHOD != "t" ]; then
         ../fasttext predict-prob $TMPFILE.bin $TMPREST $NBROFCLASSES > $TMPPROBS
      fi
   done
}

#REVERSE="-R"
run-experiment t # selection by earliest time
REVERSE=""
run-experiment r # random data selection
run-experiment c # selection by least confidence
run-experiment m # selection by smallest margin of confidence
run-experiment e # selection by highest entropy
run-experiment l # selection by highest entropy
REVERSE="-R"
run-experiment t # selection by latest time

rm -f $TMPFILE $TMPFILE.??? $TMPFILE.???? $TMPFILE.????? $TMPSTART.bin

exit 0
