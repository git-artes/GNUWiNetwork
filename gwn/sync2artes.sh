#!/bin/bash
# sync2artes.sh: synchronizes to git-artes/GNUWiNetwork
#



echo !!!
echo "Running in demo mode, nothing done!"
echo !!!

# excludes .git directories, VERY IMPORTANT
cd ..
rsync -nauv --delete --exclude=\.* --exclude=draft GWNcode/ GWNartes/ 
