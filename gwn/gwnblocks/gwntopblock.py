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
The GWN top block class.
'''

import sys, Queue, time

import gwnblocks.gwnblock as gwnblock
import gwnblocks.gwninport as gwninport

#sys.path +=sys.path + ['..']



class GWNTopBlock():
    '''Defines blocks and connections.

    This class must be subclassed. The main program must create an object of a class that inherits from this class; blocks and connections are defined in that object. The main progam can be created with GWN Companion.

    This class defines the function that connects two blocks. Blocks in GNU Wireles Network must inherit from class GWNBlock, because class GWNBlock defines the interface which this class calls to connect blocks.

    @ivar queues_size: the maximum length of the queue (or other implementation) where events are input.
    '''

    def __init__(self,queues_size=10):
        '''Constructor.

        '''        
        self.queues_size = queues_size


    def connect(self, tp_source, tp_sink):
    #def connect(self, tuple1, tuple2):
        ''' Connects a source block to a sink block.

        The source block ouputs events, the sink block inputs events. The source block writes to the Connector atttached to an InPort in the sink block.

        The source output port is a position in a list of out ports in the source block. On connection, a reference to a sink input Connector object is is placed in this position. A source object writes out an event an each and all of its out ports, i.e. on each and all of the Connector objects in the block's out ports list.

        The sink input port is an InPort object attached to the sink block. The InPort object is attached to a unique Connector object. The sink input contains a list of InPort objects, each attached to a unique Connector object.

        All events are put or got from Connector objects; Connector objects define functions put() and get() to this purpose.

        This function tries to get a reference to the InPut port in the sink object input ports list, in the position indicated as a parameter. If there is a Connector object attached to this input, it obtained. If there is no Connector object attached to this InPort, it is created and attached. In both cases, a reference to a Connector object is obtained. This reference is assigned to the list of ouput ports of the source block, in the position indicated by the parameter.

        @param tp_source: a tuple (source, source_out) where source is a Block object, source_out is a position in its output ports list.
        @param tp_sink: a tuple (sink, sink_in) where sink is a Block object, sink_in is a position in its input ports list.
        '''
        source, source_out = tp_source
        sink, sink_in = tp_sink
        conn_in = sink.get_connector_in(sink_in)
        #print conn_in
        if conn_in:
            source.set_connection_out(conn_in, sink_in)
        else:
            connector = gwninport.AQueueConnector(self.queues_size)
            sink.set_connection_in(connector, sink_in)
            source.set_connection_out(connector, source_out)



class top_block_test(GWNTopBlock):

	def __init__(self):
         GWNTopBlock.__init__(self)
         ##################################################
         # Blocks
         ##################################################
         self.source_0 = gwnblock.GWNBlock(1, 'BlockOne', 0, 1) 
         self.sink_0   = gwnblock.GWNBlock(2, 'BlockTwo', 1, 0) 
         ##################################################
         # Connections
         ##################################################
         self.connect( (self.source_0, 0), (self.sink_0, 0) )



def test():
    '''Transfers events from a source block to a sink block.
    '''
    tb = top_block_test()
    print tb.source_0
    print tb.sink_0

    #tb.source_0.ports_out[0].put('Hello')
    for i in range(0,5):
        snt_ev = 'Event' + str(i)
        print '  out from source object event %s ...' % (snt_ev,)
        tb.source_0.write_out(0, snt_ev)
        rec_ev = tb.sink_0.ports_in[0].conn.get()    
        print '  ... got from sink object event %s' % (rec_ev,)
        time.sleep(1)


if __name__ == '__main__':
    try:
        test()
    except KeyboardInterrupt:
        pass



