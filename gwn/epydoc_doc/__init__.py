#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''An Epydoc example documentation package.

Package module documentation goes in file C{__init__.py}, which may be empty but must exist to consider the present directory a "package". A module in this package is a file of extension .py in this directory. The package name is the name of the directory where its C{__ini__.py} file and other module files are contained.

Generate Epydoc documentation with the following command (C{man epydoc} for more options)::

    epydoc -v -n <project name> --exclude="<subdir1>|<subdir2>" .

This creates a directory named 'html' in the working directory.

A script to generate Epydoc documentation follows:: 

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
        epydoc -v -n $PRJNM --exclude="draft|old" .
    fi

References:

    - U{The Epytext markup language<http://epydoc.sourceforge.net/manual-epytext.html>}
    - U{Epydoc fields<http://epydoc.sourceforge.net/manual-fields.html>}
    - U{The epydoc homepage<http://epydoc.sourceforge.net>}
'''



