#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Tue May  7 11:05:17 2013

@author: belza
'''

import sys
sys.path +=['..']

import threading, Queue, time

import blocks.utilblocks.timer.timer as Timer
import gwnevents.api_events as events
import NetworkConfiguration


class Beacon(threading.Thread) :
    '''The Beacon  is a Thread.
    
    This class controls the Beacon generation.       
    '''

    def __init__(self, network_conf, tx_event_q):
        '''  
        Constructor.
        
        @param network_conf: actual network configuration.        
        @param tx_event_q: the event queue where the beacon events will be added.
        '''

        threading.Thread.__init__(self)
        self.finished = False        
        self.my_addr = network_conf. getStationId()
        self.broadcast_addr =network_conf.getBroadcastAddr()
        self.my_queue = Queue.Queue(10)
        self.my_actual_net_conf = network_conf 
        self.tx_event_q = tx_event_q
        self.activateBeacon()
       
        
    def run(self):
        while not self.finished :
            aux= self.my_queue.get()
            if aux.nickname == "TimerTimer":
                timer=Timer.Timer(self.my_queue, \
                    self.my_actual_net_conf.beacon_period, 1, "TimerTimer")
                timer.start()
                event = events.mkevent("MgmtBeacon")
                event.ev_dc['src_addr'] = self.my_addr
                event.ev_dc['dst_addr'] = self.broadcast_addr
                event.ev_dc['peerlinkId'] = 0
                self.tx_event_q.put(event,False)

    def activateBeacon(self):
        timer=Timer.Timer(self.my_queue, \
            self.my_actual_net_conf.beacon_period, 1, "TimerTimer")
        timer.start()
    
    def stop(self):
        self.finished = True
        self._Thread__stop()



def test():
    myQueue=Queue.Queue(10)
    net_conf1 = NetworkConfiguration.NetworkConfiguration(100, \
        'my network', 256, 1)
    myBeacon = Beacon(net_conf1 ,myQueue)
    myBeacon.start()
    #aux=""
    while 1:
        event= myQueue.get()
        #aux = event.ev_subtype
        print " LLEGO EVENTO ", event, " ", int(round(time.time() * 1000)) 
   
    

if __name__ == '__main__':
    try:
        test()
    except KeyboardInterrupt:
        pass


