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


'''An IEEE 802.11 framer block.
'''

import sys

#import utils.framers.ieee80211.frames as frames
import utils.framers.ieee80211.api_frmevs as api_frmevs
import gwnblocks.gwnblock as gwn



class Framer(gwn.GWNBlock):
    '''An Framer based on IEEE 802.11 frames.

    Receives an Event, generates a frame packet, assigns it to the Event object as an attribute, and outputs the Event object.
    '''

    def __init__(self):
        '''Constructor.
        '''
        super(Framer, self).__init__(1, 'Framer', 1, 1)        
        self.finished= False


    def process_data(self, port_type, port_nr, ev):
        '''Generates a frame and includes it into an ouput event.
        
        From the event received, generates a frame packet, assigns this frame packet as an atrribute to the same event, and outputs the event.
        '''
        frmobj = api_frmevs.evtofrm(ev)
        framepkt = frmobj.mkpkt()
        ev.frmpkt = framepkt
        self.write_out(0, ev)
        return



if __name__ == '__main__':
    import doctest
    testfilename = sys.argv[0][:-2] + 'txt'
    try:
        doctest.testfile(testfilename)
    except:      # no text file present
        pass


