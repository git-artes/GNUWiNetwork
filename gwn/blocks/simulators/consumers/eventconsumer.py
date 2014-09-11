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
An event consumer simulator.
'''

import sys
import time

#sys.path += ['..']
import gwnblocks.gwnblock as gwnblock
import gwnblocks.gwninport as gwninport


class EventConsumer(gwnblock.GWNBlock) :
    '''An event consumer block.
    '''

    def __init__(self, blkname):
        '''Constructor.
        
        @param blkname: the block name.
        '''
        super(EventConsumer,self).__init__(1, 'EventConsumer', 1, 0)
        self.blkname = blkname
        
    def process_data(self, port_type, port_nr, ev):
        '''This is the private thread that generates.
        '''
        if port_type == "inport":
  		    #print '--> Consumer %s received event %s' % (self.blkname, ev.__str__())
            print '--> Consumer', self.blkname, 'received event', ev


def test():
    blk1 = EventConsumer('consumer1')
    print blk1
    connector1 = gwninport.AQueueConnector()
    blk1.set_connection_in(connector1, 0)

    blk1.start()
    time.sleep(2)

    for i in xrange(0, 5):
        print connector1.put('ev' + str(i))
        time.sleep(1)

    time.sleep(8)
    blk1.stop()
    blk1.join()



if __name__ == '__main__':
    try:
        test()
    except KeyboardInterrupt:
        pass
