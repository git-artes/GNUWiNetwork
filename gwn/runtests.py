#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    This file is part of GNUWiNetwork,
#    Copyright (C) 2014 by 
#        Pablo Belzarena, Gabriel Gomez Sena, Victor Gonzalez Barbone,
#        Facultad de Ingenieria, Universidad de la Republica, Uruguay.
#
#    GNUWiNetwork is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GNUWiNetwork is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GNUWiNetwork.  If not, see <http://www.gnu.org/licenses/>.
#


# runtests.py: run doctests

import os
import os.path
import doctest

import sys
sys.path += ['.']



curdir = os.getcwd()


omitdirs = ['/old/', '/gnu/', '/gwnc/', '/html/']
lststfiles = []
# selects .txt files in directory tree except if dir in omitdirs
for dirpath, dirnames, filenames in os.walk('.'):
    for fname in filenames:
        #if fl.endswith('.py'):
        #    nmfl = fl.partition('.py')[0]
        if fname.endswith('.txt'):       # any text file, doctest or not
            tstfnm = dirpath + '/' + fname
            for omtdir in omitdirs:
                if omtdir in tstfnm:     # testfile in omitted dir
                    break
                else:
                    if tstfnm in lststfiles:   # if not repeats filenames
                        pass
                    else:
                        lststfiles += [tstfnm]
#for fl in lststfiles:
#    print fl
    
modsfail = []
for tstfl in lststfiles:
    print '=== Testing ' + tstfl + '... '
    nmdir, fname = os.path.split(tstfl)
    os.chdir(nmdir)
    #print '    EN ' + os.getcwd() + '; testing file ' + fname
    #pkg = os.path.basename(mndir)
    #print '    package: ', pkg
    #tstrslt = doctest.testfile(fname, package=pkg)

    tstrslt = doctest.testfile(fname, verbose=False, report=False)

    #tstrslt = ''
    os.chdir(curdir)
    #print '    EN ' + os.getcwd()
    attempted, failed = tstrslt.attempted, tstrslt.failed
    if attempted == 0:
        print '   Not a test file.'
        continue
    print '   Attempted: ' + str(attempted) + ', failed: ' + str(failed)
    if failed != 0:          # not all tests passed
        modsfail += [(fname, nmdir)] 
        raw_input('   Tests FAILED. Press Enter to continue.')

if len(modsfail) > 0:
    print '\nThese modules had errors:'
    for (fname, nmdir) in modsfail:
        print '   ' + fname + ' in ' + nmdir
else:
    print '\nNo modules had errors.'
print
    
    
# to select only .txt files corresponding to .py files
"""
for dirpath, dirnames, filenames in os.walk('..'):
    for fl in filenames:
        if fl.endswith('.py'):
            nmfl = fl.partition('.py')[0]
            if nmfl + '.txt' in filenames:
                nmtstfl = dirpath + '/' + nmfl + '.txt'
                for omtdir in omitdirs:
                    if omtdir in nmtstfl:
                        pass
                    else:
                        print nmtstfl
"""

