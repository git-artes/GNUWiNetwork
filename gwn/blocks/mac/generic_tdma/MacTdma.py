#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
A MAC TDMA module.
'''

import sys
sys.path +=['..']

import threading, Queue,time
import libmanagement.NetworkConfiguration as NetworkConfiguration
import gwnevents.api_events as events
import libtimer.timer as Timer
import libutils.gnlogger as gnlogger
import logging
import ControlChannel
import libvirtualchannel.EventConsumer as EventConsumer
module_logger = logging.getLogger(__name__)

class ProcessingL2Events(threading.Thread) :
    '''The TDMA MAC controller, a Thread.   

    This class controls the operation of the TDMA MAC       
    '''

    def __init__(self,network_conf,L2_ctrl_rx_q,L2_data_rx_q, L1_event_tx_q):
        '''  
        Constructor.
        
        @param network_conf: actual network configuration.        
        @param L2_ctrl_rx_q: The event queue where processes of L2 or uper layers put the control events to be processed by the MAC.
        @param L2_data_rx_q: The event queue where processes of L2 or uper layers put the data events to be processed by the MAC.
        @param L1_event_tx_q: The event queue where the MAC  puts the events to be send to other nodes.
        '''
        threading.Thread.__init__(self)
        self.my_addr = network_conf. getStationId()
        self.broadcast_addr =network_conf.getBroadcastAddr()
        self.net_conf = network_conf 
        self.L2_ctrl_rx_q = L2_ctrl_rx_q
        self.L2_data_rx_q = L2_data_rx_q
        self.L1_event_tx_q =L1_event_tx_q
        self.finished = False
        self.logger = logging.getLogger(str(self.__class__))
        self.logger.debug(str(self.my_addr)+ '.... creating an instance of ProcessingL2Events')
    
    def run(self):
        while not self.finished :
            event= self.L2_ctrl_rx_q.get()
            if event.nickname == "TimerTimer":
                self.logger.debug(str(self.my_addr)+':   Timer received in ProcessingL2Events')
                " If I have data to send, now is my time slot!!"
                if self.L2_data_rx_q.empty() == False:
                    eventData= self.L2_data_rx_q.get()
                    self.logger.debug(str(self.my_addr)+':   This is my time slot and I have data to send:  '+eventData.__str__().replace('\n',';'))
                    self.L1_event_tx_q.put(eventData,False)
                else:
                    self.logger.debug(str(self.my_addr)+':   This is my time slot and I DO NOT have data to send')
            else:
                if event.nickname == "MgmtBeacon":
                    "I have to send the control frame and is the beginning of a new set of time slots"
                    "The only one that recieves form L2 control events is the master. The master must schedule now its data transmision"
                    " The slaves will schedule its data transmission when a ctrl frame arrives from Layer 1"
                    self.logger.debug(str(self.my_addr)+':   A control event arrives and will be send to the slaves')                    
                    self.L1_event_tx_q.put(event,False)                    
                    self.time_slot = event.ev_dc['time_slot']
                    self.allocation = event.ev_dc['allocation'].index(self.my_addr)
                    self.logger.debug(str(self.my_addr)+':  Schedule a new transmission in : '+ str( self.time_slot*(self.allocation+1)) )
                    timer=Timer.Timer(self.L2_ctrl_rx_q, \
                    self.time_slot*(self.allocation+1),1,"TimerTimer")
                    timer.start()                    
                else:
                    self.logger.info(str(self.my_addr)+';  An event type not expected arrives to ProcessingL2Events' )

                     
    def stop(self):
        self.finished = True
        self._Thread__stop()      
        
        
        

class ProcessingL1CtrlEvents(threading.Thread) :
    '''The TDMA MAC controller, a Thread.   

    This class controls the operation of the TDMA MAC       
    '''

    def __init__(self,network_conf,L1_ctrl_rx_q, L2_ctrl_rx_q):
        '''  
        Constructor.
        
        @param network_conf: actual network configuration.        
        @param L2_ctrl_rx_q: The event queue where processes of L2 or uper layers put the control events to be processed by the MAC.
        @param L1_ctrl_rx_q: The event queue where L1 events are queued to be processed by the MAC.
        '''
        threading.Thread.__init__(self)
        self.my_addr = network_conf. getStationId()
        self.broadcast_addr =network_conf.getBroadcastAddr()
        self.net_conf = network_conf 
        self.L1_ctrl_rx_q = L1_ctrl_rx_q
        self.L2_ctrl_rx_q = L2_ctrl_rx_q        
        self.finished = False
        self.logger = logging.getLogger(str(self.__class__))
        self.logger.debug(str(self.my_addr)+'....  creating an instance of ProcessingL1CtrlEvents')
    
    def run(self):
        while not self.finished :
            event= self.L1_ctrl_rx_q.get()
            if event.nickname == "MgmtBeacon":
                    "This control frame indicates that is the begging of a new set of slots"
                    "If I am the source of this frame, the frame is deleted"
                    " The slaves will schedule its data transmission when a ctrl frame arrives from Layer 1"
                    self.logger.debug(str(self.my_addr)+':  A control event arrives from L1:  '+event.__str__().replace('\n',';')) 
                    if event.ev_dc['src_addr'] != self.my_addr:
                        self.time_slot = event.ev_dc['time_slot']
                        self.allocation = event.ev_dc['allocation'].index(self.my_addr)
                        self.logger.debug(str(self.my_addr)+';  Schedule a new transmission in : '+ str( self.time_slot*(self.allocation+1)) )
                        timer=Timer.Timer(self.L2_ctrl_rx_q, \
                        self.time_slot*(self.allocation+1),1,"TimerTimer")
                        timer.start()
                    else:
                        self.logger.debug(str(self.my_addr)+':   I am the source of a Ctrl event, the event is ignored')
            else:
                    self.logger.info(str(self.my_addr)+':   An event of unexpected type arrives to ProcessingL1CtrlEvents' )

    def stop(self):
        self.finished = True
        self._Thread__stop()      

class ProcessingL1DataEvents(threading.Thread) :
    '''The TDMA MAC controller, a Thread.   

    This class controls the operation of the TDMA MAC       
    '''

    def __init__(self,network_conf,L1_data_rx_q,L2_event_tx_q):
        '''  
        Constructor.
        
        @param network_conf: actual network configuration.        
        @param L2_ctrl_rx_q: The event queue where processes of L2 or uper layers put the control events to be processed by the MAC.
        @param L2_data_rx_q: The event queue where processes of L2 or uper layers put the data events to be processed by the MAC.
        @param L1_event_tx_q: The event queue where the MAC  puts the events to be send to other nodes.
        '''
        threading.Thread.__init__(self)
        self.my_addr = network_conf. getStationId()
        self.broadcast_addr =network_conf.getBroadcastAddr()
        self.net_conf = network_conf 
        self.L1_data_rx_q = L1_data_rx_q
        self.L2_event_tx_q =L2_event_tx_q        
        self.finished = False
        self.logger = logging.getLogger(str(self.__class__))
        self.logger.debug(str(self.my_addr)+'.....creating an instance of ProcessingL1DataEvents')
    
    def run(self):
        while not self.finished :
            event= self.L1_data_rx_q.get()
            if event.nickname == "DataData":
                    "When a data frame is received the data is transmited to L2_tx in order to be processed"
                    "For the moment there is not ACK frame, future work"
                    "If the source is my address the data event is ignored"
                    if event.ev_dc['src_addr'] != self.my_addr:
                        self.L2_event_tx_q.put(event,False)
                        self.logger.debug(str(self.my_addr)+':   A data event arrives from L1;:  '+event.__str__().replace('\n',';')) 
                    else:
                        self.logger.debug(str(self.my_addr)+':   I am the source of a Data event, the event is ignored')
            else:
                    self.logger.info(str(self.my_addr)+':  An event of unexpected type arrives to ProcessingL1DataEvents' )

    def stop(self):
        self.finished = True
        self._Thread__stop()      



class MacTdma(threading.Thread) :
    '''The TDMA MAC controller, a Thread.   

    This class controls the operation of the TDMA MAC       
    '''

    def __init__(self,network_conf,L1_ctrl_rx_q,L1_data_rx_q,L2_ctrl_rx_q,L2_data_rx_q,L1_event_tx_q,L2_event_tx_q,master=False):
        '''  
        Constructor.
        
        @param network_conf: actual network configuration.        
        @param L1_ctrl_rx_q: The event queue where the lower layers put the control events from other nodes.
        @param L1_data_rx_q: The event queue where the lower layers put the data events from other nodes.
        @param L2_ctrl_rx_q: The event queue where processes of L2 or uper layers put the control events to be processed by the MAC.
        @param L2_data_rx_q: The event queue where processes of L2 or uper layers put the data events to be processed by the MAC.
        @param L1_event_tx_q: The event queue where the MAC  puts the events to be send to other nodes.
        @param L2_event_tx_q: The event queue where the MAC  puts the events to be send to L2 processes or uper layers.        
        '''
        threading.Thread.__init__(self)
        self.my_addr = network_conf. getStationId()      
        self.logger = logging.getLogger(str(self.__class__))
        self.logger.debug(str(self.my_addr)+'...........creating an instance of MacTdma')
       
        self.broadcast_addr =network_conf.getBroadcastAddr()
        self.net_conf = network_conf 
        self.L1_ctrl_rx_q = L1_ctrl_rx_q
        self.L1_data_rx_q = L1_data_rx_q
        self.L2_ctrl_rx_q = L2_ctrl_rx_q
        self.L2_data_rx_q = L2_data_rx_q
        self.L1_event_tx_q =L1_event_tx_q
        self.L2_event_tx_q =L2_event_tx_q        
        self.proc_l2_ev = ProcessingL2Events(self.net_conf,self.L2_ctrl_rx_q,self.L2_data_rx_q,self.L1_event_tx_q)
        self.proc_l2_ev.start()
        self.proc_l1_ctrl_ev = ProcessingL1CtrlEvents(self.net_conf,self.L1_ctrl_rx_q,self.L2_ctrl_rx_q)
        self.proc_l1_ctrl_ev.start()
        self.proc_l1_data_ev = ProcessingL1DataEvents(self.net_conf,self.L1_data_rx_q,self.L2_event_tx_q)
        self.proc_l1_data_ev.start()
        self.master = master
        if self.master == True:
            self.myControl = ControlChannel.ControlChannel(self.net_conf ,L2_ctrl_rx_q)
            self.myControl.start()
            



    def stop(self):
        self.proc_l2_ev.stop()
        self.proc_l1_ctrl_ev.stop()
        self.proc_l1_data_ev.stop()
        if self.master == True :
            self.myControl.stop()
            self.myControl.join()
        self.proc_l2_ev.join()
        self.proc_l1_ctrl_ev.join()
        self.proc_l1_data_ev.join()
        

def test1():
    gnlogger.logconf()         # initializes the logging facility
    module_logger.info('start this module')
    L1_ctrl_rx_q = Queue.Queue(10)
    L1_data_rx_q = Queue.Queue(10)
    L2_ctrl_rx_q = Queue.Queue(10)
    L2_data_rx_q = Queue.Queue(10)
    L1_event_tx_q = Queue.Queue(10)
    L2_event_tx_q = Queue.Queue(10)                
    net_conf1 = NetworkConfiguration.NetworkConfiguration(100,'my network',256,1)
    net_conf1.slots = 3 
    " The first slot  is the control slot, the others are for data"
    net_conf1.control_time = 3
    " Each slot has 1 second"
    net_conf1.list_nodes.append(100)
    net_conf1.list_nodes.append(101)
    
    mac_control = MacTdma(net_conf1,L1_ctrl_rx_q,L1_data_rx_q,L2_ctrl_rx_q,L2_data_rx_q,L1_event_tx_q,L2_event_tx_q,True)
    event = events.mkevent("DataData")
    event.ev_dc['src_addr'] = 100 
    event.ev_dc['dst_addr'] = 101 
    L2_data_rx_q.put(event,False)

    time.sleep(5)
    mac_control.stop()
   

def test2():
    gnlogger.logconf()         # initializes the logging facility
    module_logger.info('start this module')
    L1_ctrl_rx_q = Queue.Queue(10)
    L1_data_rx_q = Queue.Queue(10)
    L2_ctrl_rx_q = Queue.Queue(10)
    L2_data_rx_q = Queue.Queue(10)
    L1_event_tx_q = Queue.Queue(10)
    L2_event_tx_q = Queue.Queue(10)                
    net_conf1 = NetworkConfiguration.NetworkConfiguration(101,'my network',256,1)

    
    mac_control = MacTdma(net_conf1,L1_ctrl_rx_q,L1_data_rx_q,L2_ctrl_rx_q,L2_data_rx_q,L1_event_tx_q,L2_event_tx_q,False)

    event = events.mkevent("DataData")
    event.ev_dc['src_addr'] = 101
    event.ev_dc['dst_addr'] = 100
    L2_data_rx_q.put(event,False)
    time.sleep(10)
    event = events.mkevent("MgmtBeacon")
    net_conf1.slots = 3 
    " The first slot  is the control slot, the others are for data"
    net_conf1.control_time = 3
    " Each slot has 1 second"
    net_conf1.list_nodes.append(101)
    net_conf1.list_nodes.append(100)
    event.ev_dc['src_addr'] = 100
    event.ev_dc['dst_addr'] = net_conf1.broadcast_addr
    event.ev_dc['time_slot']=  net_conf1.control_time/ net_conf1.slots
    event.ev_dc['allocation'] = net_conf1.list_nodes
    L1_ctrl_rx_q.put(event,False)
    time.sleep(5)
    mac_control.stop()
   
def test3():
    gnlogger.logconf()         # initializes the logging facility
    module_logger.info('start this module')
    L1_ctrl_rx_q = Queue.Queue(10)
    L1_data_rx_q = Queue.Queue(10)
    L2_ctrl_rx_q = Queue.Queue(10)
    L2_data_rx_q = Queue.Queue(10)
    L1_event_tx_q = Queue.Queue(10)
    L2_event_tx_q = Queue.Queue(10)                
    net_conf1 = NetworkConfiguration.NetworkConfiguration(101,'my network',256,1)
#    net_conf1.slots = 3 
#    " The first slot  is the control slot, the others are for data"
#    net_conf1.control_time = 3
#    " Each slot has 1 second"
#    net_conf1.list_nodes.append(101)
#    net_conf1.list_nodes.append(100) 
    mac_control = MacTdma(net_conf1,L1_ctrl_rx_q,L1_data_rx_q,L2_ctrl_rx_q,L2_data_rx_q,L1_event_tx_q,L2_event_tx_q,False)
    event = events.mkevent("DataData")
    event.ev_dc['src_addr'] = 100
    event.ev_dc['dst_addr'] = 101
    L1_data_rx_q.put(event,False)
    myConsumer = EventConsumer.EventConsumer("L3consumer",L2_event_tx_q)
    myConsumer.start()
    time.sleep(5)
    mac_control.stop()
    myConsumer.stop() 
    
if __name__ == '__main__':
    try:
        test1()
        test2()
        test3()
    except KeyboardInterrupt:
        pass



