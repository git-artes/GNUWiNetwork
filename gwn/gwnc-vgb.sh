#!/bin/bash
# gnuradio-companion.sh: invokes script of same name in subdir

PYTHONPATH=$PYTHONPATH:/homensk/victor/IIE/GWNcode/gwn

THISDIR=`pwd`
cd ./gwnc/scripts
python ./gwn-companion.py
cd $THISDIR
