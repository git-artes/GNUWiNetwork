#!/bin/bash
# gnuradio-companion.sh: invokes script of same name in subdir

THISDIR=`pwd`
cd ./gwnc/scripts
python ./gwn-companion.py
cd $THISDIR
