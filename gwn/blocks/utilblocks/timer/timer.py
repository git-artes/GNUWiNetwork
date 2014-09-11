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
A timer block.
'''

import sys
import time

sys.path += sys.path + ['..']
import gwnevents.api_events as events
import gwnblocks.gwnblock as gwn
import gwnblocks.gwninport as inport



class Timer(gwn.GWNBlock):
    '''A timerthat waits an interval and generates a Timer Event.

    This class is a timer that waits for a given interval. After that generates an event of Yype TIMER and Subtype the name given in subTypeEvent1.
    The timer retries the number of times gven in the parameter retry. After the given number of retries it generates the event of Type TIMER and subtype given in subTypeEvent2 if it is not None.
    '''

    def __init__(self, interval=1, retry=1, nickname1="TimerTimer", nickname2=None, \
            add_info=None):
        '''Constructor.
        
        @param interval: the interval of time.
        @param retry: the number of retries.
        @param nickname1: the nickname of the event that must be called after each retry.
        @param nickname2: the nickname of the event that must be called after the given number of retries.
        @param add_info: additional information that will be send with the Timer Event.
        '''        
        # The Timer has one output and 0 inputs so we must call the father constructor\
        #   with parameters (0,1)"
        super(Timer,self).__init__(1, "Timer1", 1, 1, 1)
        self.interval = interval
        self.retry = retry
        self.nickname1 = nickname1
        self.nickname2 =nickname2
        self.add_info = None
        self.set_timer(0, False, self.interval, self.retry, self.nickname1, \
            self.nickname2, self.add_info)
        
    def process_data(self, port_type, port_nr, ev):
        '''This is the private thread that generates.
        '''
        if port_type == "intimer":
            self.write_out(0, ev)
        elif port_type == "inport":
            if ev.nickname == 'TimerConfig':
                #print "Receive configuration event ",  event
                self.set_config(ev)
                self.set_timer(0, interrupt=True)
                self.set_timer(0, False, self.interval, self.retry, self.nickname1, \
                    self.nickname2, self.add_info)
            else:
                print " \n Received event %s in port %s %d:" % (ev, port_type, port_nr)
        else:
            pass
            

    def set_config(self, event):
        if 'interval' in event.ev_dc:
            self.interval = event.ev_dc['interval']
        if 'retry' in event.ev_dc:
            self.retry = event.ev_dc['retry']
        if 'nickname1' in event.ev_dc:
            self.nickname1 = event.ev_dc['nickname1']
        if 'nickname2' in event.ev_dc:
            self.nickname2 = event.ev_dc['nickname2']
        else:
            self.nickname2 = None
        if 'add_info' in event.ev_dc:
            self.add_info = event.ev_dc['add_info']
        else:
            self.add_info = None


def test2():
    '''Test InPort, Block classses.
    '''
    blk1 = Timer()
    print blk1
    connector1 = inport.AQueueConnector()
    connector2 = inport.AQueueConnector()
    #blk1.start()
    #time.sleep(2)
    blk1.set_connection_in(connector1,0)
    blk1.set_connection_out(connector1,0)
    blk1.start()
    time.sleep(3)
    event = events.mkevent("TimerConfig")
    event.ev_dc['interval'] = 1
    event.ev_dc['retry'] = 5
    event.ev_dc['nickname1'] = "TimerTOR1"
    connector1.put(event)
        
    time.sleep(10)
    blk1.stop()
    blk1.join()
    #blk1.stop()

 
    

if __name__ == '__main__':
    try:
        test2()
    except KeyboardInterrupt:
        pass




