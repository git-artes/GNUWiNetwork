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


'''An IEEE 802.11 deframer block.
'''


import sys

import gwnblocks.gwnblock as gwn

import utils.framers.ieee80211.api_frmevs as api_frmevs
import utils.framers.ieee80211.api_frames as api_frames


class Deframer(gwn.GWNBlock):
    '''A frame to event scheduler, based on IEEE 802.11 frames.

    A block that receives a frame packet, generates and Event object from it, and outputs this Event object.
    '''
    def __init__(self):
        '''Constructor
        '''
        super(Deframer,self).__init__(1, 'Deframer', 1, 1)
        self.finished = False


    def process_data(self, port_type, port_nr, ev):
        '''Reads frames, outputs events by type.
        
        Receives a frame packet, generates another Event object with data extracted from the frame packet, and outputs the generated Event.
        '''
        print "recibi event : ", ev
        if ev:
            frm_obj = api_frames.objfrompkt(ev.frmpkt)
            ev_out = api_frmevs.frmtoev(frm_obj)
            if ev_out != None:
                self.write_out(0, ev_out)
            else:
                raise frames.EventFrameException('Deframer, error in frame')
        else:
            print " Not event recieved"

if __name__ == '__main__':
    import doctest
    testfilename = sys.argv[0][:-2] + 'txt'
    try:
        doctest.testfile(testfilename)
    except:      # no text file present
        pass

