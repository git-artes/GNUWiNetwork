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
The GWN generic block class.
'''

import threading, Queue, time
import sys

#from gwninport import *   # suppress after qulifying all gwninport items
import gwninport
import gwnintimer

#sys.path += sys.path + ['..']

#thread_lock = threading.Lock()  # not used in this module



class GWNBlock(threading.Thread):
    '''The main block. All blocks inherit from it.
    '''

    def __init__(self, blkid, blkname, number_in=0,number_out=0, number_timers=0):
        '''  
        Constructor.
        
        @param number_in: the number of input ports of this block.
        @param number_out: the number of output ports of this block.
        @param number_timers: a list of timers. TODO: may become tuples to build timers.
        '''        
        threading.Thread.__init__(self)
        self.blkid = blkid
        self.blkname = blkname
        self.ports_in = []
        self.ports_out = []
        self.timers = []
        self.finished = False
        self.set_in_size(number_in)
        self.set_out_size(number_out)
        self.set_timer_size(number_timers)


    def set_in_size(self, number_in):
        '''Creates a list of input connections.

        Creates a list of InPort instances; each InPort instances will be later assigned a Connector instance to implement the input connection.
        @param number_in: the number of input connections.
        '''
        for i in xrange(0, number_in):
            port = gwninport.InPort(self, i)
            print port
            self.ports_in.append(port)


    def set_out_size(self,number_out):
        '''Creates a list of output connections.

        Creates a lists of empty lists; each of the empty lists is an output connection.
        @param number_out: the number of output connections.
        '''
        self.ports_out = [[] for x in xrange(0,number_out)]


    def set_timer_size(self, number_timers):
        '''Creates InTimer instances, assigns to block.

        Creates a list of InTimer objects with default values; timer characteristics can be set later with function set_timer().
        @param number_timers: the number of timers.
        '''
        for i in xrange(0, number_timers):
            mytimer = gwnintimer.InTimer(self, i)
            print mytimer
            self.timers.append(mytimer)


    def set_timer(self, index, interrupt=True, interval=1, retry=1, \
            nickname1="TimerTimer", nickname2=None, add_info=None):
        '''Sets timer values.

        @param index: the timer index position.
        @param interrupt: if True interrupts timer event generation until set to False.
        @param interval: the time elapsed between two successively generated timer events.
        @param retry: the number of events to be generated; once this number is reached, the timer is interrupted until explicitly told to resume even generation.
        @param nickname1: the nickname of the event to be generated after each interval.
        @param nickname2: the nickname of the event to be generated once reached the retry number.
        @param add_info: additional info.
        ''' 
        mytimer = self.timers[index]        
        mytimer.interval = interval
        mytimer.retry = retry
        mytimer.nickname1 = nickname1
        mytimer.nickname2 = nickname2 
        mytimer.add_info = add_info
        mytimer.interrupt = interrupt


    def get_port_in(self,index):
        '''Returns an input port in this block.

        Returns the InPort instance assigned to this block placed in the position indicated by index.
        @param index: the position of the input port in this block.
        '''
        return self.ports_in[index]


    def get_connector_in(self,index):
        '''Returns the connector of an input port in this block.

        Returns the Connector instance assigned to the InPort instance in this block placed in the position indicated by index.
        @param index: the position of the input port in this block.
        '''
        return self.ports_in[index].conn


    def set_connection_in(self, connector, index):
        '''Sets an input connection to a port in this block.

        Assigns a Connector instance to the InPort instance in this block placed in the position indicated by indes.
        @param connector: a Connector instance.
        @param index: the position of the input port in this block.
        '''
        if index <= len(self.ports_in)-1:
            self.ports_in[index].connect(connector)


    def set_connection_out(self, connector, index):
        '''Sets an ouput connection from this block.

        A Connector instance is assigned as an output connection from this block, in the position indicated by index.
        @param connector: a reference to a Connector object.
        @param index: the position of the output port in this block.
        '''
        if index <= len(self.ports_out)-1:
            self.ports_out[index].append(connector)


    def write_out(self, port_nr, ev):
        '''Send (write) events on all connections of an output port.

        @param port_nr: the output por number, an index of the output ports list.
        @param ev: an Event object.
        '''
        #for q in self.ports_out[port_nr]:
        for conn in self.ports_out[port_nr]:
            conn.put(ev)

            
    def run(self):
        '''Run this thread.'''
        print "Starting " + self.blkname
        for port in self.ports_in:
            port.start()

        for timer in self.timers:
            timer.start()

        for port in self.ports_in:
            port.join()


        for timer in self.timers:
            timer.join()
        return


    def stop(self):
        '''Stops ports, timers, then stops block.
        '''
        #self.exitFlag = 1
        print "Stopping " + self.blkname + '... '
        for port in self.ports_in:
            port.stop()
        for timer in self.timers:
            timer.stop()
        print self.blkname + ' stopped.'
        return


    ### user defined process code
    ###
    def process_data(self, port_type, port_nr, ev):
        '''Block specific processing.

        @param port_type: the type of port, a string.
        @param port_nr: the port number on which the event was received.
        @param ev: an Event object.
        '''
        print 'Processing, block %s, port %s %d, event %s... ' % \
            (self.blkname, port_type, port_nr, ev),
        #print '          ', self.ports[port_nr].conn.lsevents
        #time.sleep(1)
        #print ' done with event %s' % (ev,)
        print 'done.'
        return
    ###
    ### end user defined process code


    def __str__(self):
        ss = 'Block %s, %d in_ports, %d out_ports, %d timers\n' % \
            (self.blkname, len(self.ports_in), len(self.ports_out), len(self.timers))
#        for port in self.ports_in:
#            ss = ss + '  in_port %d in block %s\n' % (port.port_nr, port.block.blkname)
#        for i in range(len(self.ports_out)):   # no port_nr in ports_out
#            ss = ss + '  out_port %d in block %s\n' % \
#                (i, self.ports_out[i])
#        for timer in self.timers:
#            ss = ss + '  timer  in block \n', timer.port_nr, timer.block.blkname
        return ss



if __name__ == '__main__':
    print 'gwnblock: tests in gwntests, please do'
    print '   python gwntests.py'

