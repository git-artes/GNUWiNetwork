#!/bin/bash
# runtests.sh: run Python doctest test modules
#

INDIR=`pwd`
if [ ! -z "$1" ]
then
    DIR=$1
else
    DIR='.'
fi

cd $DIR
LSMODS=`ls *.txt`
for MOD in $LSMODS
  do
  echo '=== Testing' $MOD
  python -m doctest $MOD
  echo
  done
cd $INDIR
  


