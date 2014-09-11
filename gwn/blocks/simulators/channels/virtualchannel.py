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


'''
A virtual channel simulator.
'''

import sys
import random

#sys.path +=sys.path + ['..']
#from libutils.gwnscheduler2 import Scheduler
import gwnblocks.gwnblock as gwnblock



class GWNVirtualChannel(gwnblock.GWNBlock):
    '''A virtual channel emulating frame loss.
    '''


    def __init__(self, frame_loss):
        ''' Constructor.
        
        @param frame_loss: rate of frame loss, in [0, 1]; 0 is no loss, all frames transferred; 1 is total loss, no frame transferred.
        '''        
        super(GWNVirtualChannel, self).__init__(1, 'VirtualChann1', 1, 1)
        self.frame_loss = frame_loss        
        self.finished = False


    def process_data(self, port_type, port_nr, ev):
        '''Transfers event from input to output with probability of loss.
        '''
        a = random.random()
        if a > self.frame_loss:
            self.write_out(0, ev)
        return



