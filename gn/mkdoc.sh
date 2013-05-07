#!/bin/bash
# mkdoc.sh: makes epydoc

if [ ! "$1" ]
then
  echo "Usage: mkdoc.sh <project name>"
else
  PRJNM="$1"
  if [ -d "html" ]
  then
    rm -r html/*
  else 
    mkdir html
  fi
  epydoc -v -n $PRJNM --exclude="viejos|otros|old|others|draft" .
fi
