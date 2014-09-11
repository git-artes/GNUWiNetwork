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
An event generator simulator.
'''

import sys
import time

#sys.path +=['..']
import gwnevents.api_events as events
import gwnblocks.gwnblock as gwnblock
import gwnblocks.gwninport as gwninport



class EventSimulator(gwnblock.GWNBlock) :
    '''An event generator.
    '''

    def __init__(self, interval, retry, nickname, param1=0, param2=0, param3=0):
        '''Constructor.

        TODO: substitute param1, param2, param3 for **kwords?
        TODO: unify event generation into a single function for all event types.
        @param interval: the time elapsed between two successive events.
        @param retry: the number of events to be generated.
        @param nickname: the nickname of the events to be generated.
        @param param1: param for event generation.
        @param param2: param for event generation.
        @param param3: param for event generation.
        '''
        super(EventSimulator,self).__init__(1, "Simulator1", 0, 1, 1)        
        self.finished = False    
        self.nickname =nickname
        self.param1 = param1
        self.param2 = param2
        self.param3 = param3
        self.interval = interval
        self.retry = retry
        self.set_timer(0, False, self.interval, self.retry)


    def process_data(self, port_type, port_nr, ev):
        if port_type == "intimer":
            if self.nickname=="DataData":
                event = self.event_data()
            if self.nickname=="CtrlRTS":
                event = self.event_RTS()
            if self.nickname=="CtrlCTS":
                event = self.event_CTS()
            if self.nickname=="CtrlACK":
                event = self.event_ACK()
            if self.nickname=="TimerConfig":      
                event= self.event_timer_config()
            print 'eventsimulator3', event.nickname
            self.write_out(0,event)
        else:
            pass
    
   
    def event_data(self):
        event = events.mkevent(self.nickname)
        event.ev_dc['src_addr'] = self.param1
        event.ev_dc['dst_addr'] = self.param2
        length = self.convert_int(self.param3)
        event.ev_dc['frame_length'] = length                         
        event.payload='1'*length
        return event            
        
    def event_RTS(self):
        event = events.mkevent(self.nickname)
        event.ev_dc['src_addr'] = self.param1
        event.ev_dc['dst_addr'] = self.param2
        return event        

    def event_CTS(self):
        event = events.mkevent(self.nickname)
        event.ev_dc['src_addr'] = self.param1
        event.ev_dc['dst_addr'] = self.param2
        return event

    def event_ACK(self):
        event = events.mkevent(self.nickname)
        event.ev_dc['src_addr'] = self.param1
        event.ev_dc['dst_addr'] = self.param2
        return event        

    def event_timer_config(self):
        event = events.mkevent(self.nickname)
        interval = self.convert_float(self.param1)
        event.ev_dc['interval']=interval
        retry = self.convert_int(self.param2)
        event.ev_dc['retry']=retry
        event.ev_dc['nickname1']= self.param3
        return event

    def convert_int(self,param):
        '''Convert int parameter types.
        '''
        if isinstance(param, int):
            return(param)
        else:
            if isinstance(param, str):
                if param.isdigit():
                    return(int(param))

        return(0)
        
        
    def convert_float(self,param):
        '''Convert int parameter types.
        '''
        if isinstance(param, float):
            return(param)
        else:
            if isinstance(param, str):
                try:
                    return(float(param))
                except ValueError:
                    return(0)
        return(0)
        

def test2():
    '''Test EventSimulator.
    '''
    blk1 = EventSimulator(2, 5, "CtrlRTS", 100, 101)
    print blk1
    connector2 = gwninport.AQueueConnector()
    #blk1.start()
    #time.sleep(2)

    blk1.set_connection_out(connector2, 0)
    blk1.start()
    i = 1    
    while i < 10:
        i = i + 1
        print connector2.get()
        
   
    time.sleep(10)
    blk1.stop()
    blk1.join()
    #blk1.stop()

 
    

if __name__ == '__main__':
    try:
        test2()
    except KeyboardInterrupt:
        pass


