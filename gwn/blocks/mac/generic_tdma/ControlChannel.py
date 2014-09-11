#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
A control channel block.
'''

import sys
sys.path +=['..']
import libtimer.timer as Timer
import gwnevents.api_events as events
import threading,Queue,time
import libmanagement.NetworkConfiguration as NetworkConfiguration
import libutils.gnlogger as gnlogger
import logging

class ControlChannel(threading.Thread) :
    '''
    This class controls the Control Events generation.       
    '''

    def __init__(self,network_conf,tx_event_q):
        '''  
        Constructor.
        
        @param network_conf : actual network configuration.        
        @param tx_event_q : The event queue where the Control events will be added.
        '''

        threading.Thread.__init__(self)
        self.my_addr = network_conf. getStationId()
        self.logger = logging.getLogger(str(self.__class__))
        self.logger.debug(str(self.my_addr)+'...........creating an instance of Control Channel')
        self.finished = False        
        
        self.broadcast_addr =network_conf.getBroadcastAddr()
        self.my_queue = Queue.Queue(10)
        self.my_actual_net_conf = network_conf 
        self.tx_event_q =tx_event_q
        self.activateControlEvents()
       
        
    def run(self):
        while not self.finished :
            aux= self.my_queue.get()
            if aux.nickname == "TimerTimer":
                timer=Timer.Timer(self.my_queue, \
                    self.my_actual_net_conf.control_time,1,"TimerTimer")
                timer.start()
                event = events.mkevent("MgmtBeacon")
                event.ev_dc['src_addr'] = self.my_addr
                event.ev_dc['dst_addr'] = self.broadcast_addr
                event.ev_dc['time_slot']=  self.my_actual_net_conf.control_time/ self.my_actual_net_conf.slots
                event.ev_dc['allocation'] = self.my_actual_net_conf.list_nodes
                self.tx_event_q.put(event,False)

    def activateControlEvents(self):
        timer=Timer.Timer(self.my_queue, \
            self.my_actual_net_conf.control_time,1,"TimerTimer")
        timer.start()
        self.logger.debug(str(self.my_addr)+' Control Channel activate control events')
    
    def stop(self):
        self.finished = True
        self._Thread__stop()



def test():
    myQueue=Queue.Queue(10)
    net_conf1 = NetworkConfiguration.NetworkConfiguration(100,'my network',256,1)
    net_conf1.slots = 3 
    " The first slot  is the control slot, the others are for data"
    net_conf1.control_time = 3
    " Each slot has 1 second"
    net_conf1.list_nodes.append(100)
    net_conf1.list_nodes.append(101)
    myControl = ControlChannel(net_conf1 ,myQueue)
    myControl.start()
    aux=""
    while 1:
        event= myQueue.get()
        print " LLEGO EVENTO ", event, " ", int(round(time.time() * 1000)) 
   
    

if __name__ == '__main__':
    try:
        test()
    except KeyboardInterrupt:
        pass


