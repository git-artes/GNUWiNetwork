#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Mon Dec 10 14:55:52 2012

@author: belza
'''

import sys
sys.path +=['..']

import threading, Queue,time

import PeersTable, NetworkConfiguration
import gwnevents.api_events as events


class DiscoveryPeeringController(threading.Thread) :
    '''The discovery and peering controller, a Thread.   

    This class control the entries of the peers table and the set of the state machines. Each peer link has associated one state machine,       
    '''

    def __init__(self,network_conf,net_profile,q_event,tx_event_q):
        '''  
        Constructor.
        
        Each peer link has an identifier local_linkId, assigned when the peer link is created. It is inicialized when the class is created.
        @param network_conf: actual network configuration.        
        @param  net_profile: network profile.        
        @param q_event: The event queue where this object gets the events to be precessed.        
        @param tx_event_q: The event queue where to put the new events.
        '''
        threading.Thread.__init__(self)
        self.my_addr = network_conf. getStationId()
        self.broadcast_addr =network_conf.getBroadcastAddr()
        self.my_profile = net_profile
        self.my_peers = PeersTable.PeersTable()
        # each peer link has an identifier local_linkId, assigned when the peer
        # link is created. It is inicialized when the class is created."
        self.local_linkId=0          
        self.net_conf = network_conf 
        self.my_queue = q_event
        self.tx_event_q =tx_event_q
        self.finished = False
      
   
    def run(self):
        while not self.finished :
            event= self.my_queue.get()
            if event.ev_type == "Timer":
                print "Evento Timer: ", event, '\n'
                sm= self.my_peers.getSM(localLinkId = event.ev_dc['add_info'] )
                sm.fsm.process(event.ev_subtype) 
                self.my_peers.printPeersTable()
            else:
                if event.ev_type == "Mgmt":        
                    if (event.ev_dc['dst_addr'] == self.my_addr or \
                        event.ev_dc['dst_addr'] == self.broadcast_addr) and \
                        event.ev_dc['src_addr'] != self.my_addr :
                        # in this case the destination mac is my mac or is a
                        # broadcast packet and I am not the source 
                        if self.my_peers.isMember( \
                            peerMACaddr = event.ev_dc['src_addr']):
                            # in this case peer link exists in peers table
                            #print "Evento 1:", event,'  my mac: ',self.my_addr, '\n'
                            #self.my_peers.printPeersTable()                
                            sm = self.my_peers.getSM( \
                                peerMACaddr= event.ev_dc['src_addr'])
                            self.my_peers.updatePeerLinkId( \
                                event.ev_dc['src_addr'], event.ev_dc['peerlinkId'])
                            self.moveFSM(event,sm)
                            self.my_peers.printPeersTable()
                        else:
                            #print "LLEGO EVENTO ................................", event
                            # in this case peer link does not exist in peer table
                            #print "Evento 2: ", event,'  my mac: ',self.my_addr,'\n'
                            #self.my_peers.printPeersTable()
                            self.local_linkId = self.local_linkId + 1
                            self.my_peers.add(event.ev_dc['src_addr'], \
                                self.my_queue, self.tx_event_q, self.net_conf, \
                                    self.local_linkId, event.ev_dc['peerlinkId'])
                            self.net_conf.number_of_peering = \
                                self.net_conf.number_of_peering + 1
                            sm = self.my_peers.getSM(peerMACaddr = \
                                event.ev_dc['src_addr'])
                            self.moveFSM(event,sm)
                            #print "Evento 3: ", event,'  my mac: ',self.my_addr,'\n'
                            self.my_peers.printPeersTable()
                    else:
                        
                        print "Error: wrong MAC address, destination address:", \
                            event.ev_dc['dst_addr'], " source address : ", \
                            event.ev_dc['src_addr']," my address : ", \
                            self.my_addr               
    
                else: 
                    print "Error: wrong event type"
                    
    def moveFSM(self,event,sm):
        if event.nickname == "MgmtBeacon" and \
            self.net_conf.accepting_additional_peerings:
            sm.fsm.process("ACTOPN")
        if event.nickname == "ActionConfirm":                  
            sm.fsm.process("CNF_ACPT")
        if event.nickname == "ActionClose":
            sm.fsm.process("CLS_ACPT")
        if event.nickname == "ActionOpen" :
            if self.net_conf.accepting_additional_peerings:
                sm.fsm.process("OPN_ACPT")
            else:
                sm.fsm.process("OPN_RJCT")                                    

    def stop(self):
            self.finished = True
            self._Thread__stop()




def test():
    tx_event_q=Queue.Queue(10)
    event_q=Queue.Queue(10)
    net_conf1 = NetworkConfiguration.NetworkConfiguration(100,'my network',256,1)
    net_conf1.retry_timeout = 5    
    dpcontrol = DiscoveryPeeringController(net_conf1,None,event_q,tx_event_q)
    dpcontrol.start()

#    " Test1: Beacon  Confirm Open "
#    event = events.mkevent("MgmtBeacon")
#    event.src_addr=101
#    event.dst_addr= net_conf1.broadcast_addr
#    event.peerlinkId = 0
#    event_q.put(event,False)
#    time.sleep(5)
#    dpfsm = dpcontrol.my_peers.getSM(peerMACaddr= 101)
#
#    print "state", dpfsm.fsm.current_state
#    event = events.mkevent("ActionConfirm")
#    event.src_addr=101
#    event.dst_addr= 100
#    event.peerlinkId = 0
#    event_q.put(event,False)
#    time.sleep(5)
#    print "state", dpfsm.fsm.current_state
#    
#    event = events.mkevent("ActionOpen")
#    event.src_addr=101
#    event.dst_addr= 100
#    event.peerlinkId = 0
#    event_q.put(event,False)
#    time.sleep(5)
#    print "state", dpfsm.fsm.current_state
    
#    " Test2: Open  Confirm "
#    event = events.mkevent("ActionOpen")
#    event.src_addr=101
#    event.dst_addr= net_conf1.broadcast_addr
#    event.peerlinkId = 0
#    event_q.put(event,False)
#    time.sleep(5)
#    dpfsm = dpcontrol.my_peers.getSM(peerMACaddr= 101)
#
#    print "state", dpfsm.fsm.current_state
#    event = events.mkevent("ActionConfirm")
#    event.src_addr=101
#    event.dst_addr= 100
#    event.peerlinkId = 0
#    event_q.put(event,False)
#    time.sleep(5)
#    print "state", dpfsm.fsm.current_state
    
    # Test3: Beacon  Open Confirm
    event = events.mkevent("MgmtBeacon")
    event.ev_dc['src_addr'] = 101
    event.ev_dc['dst_addr'] = net_conf1.broadcast_addr
    event.ev_dc['peerlinkId'] = 0
    event_q.put(event,False)
    time.sleep(5)
    dpfsm = dpcontrol.my_peers.getSM(peerMACaddr = 101)

    event = events.mkevent("ActionOpen")
    event.ev_dc['src_addr'] = 101
    event.ev_dc['dst_addr'] = 100
    event.ev_dc['peerlinkId'] = 0
    event_q.put(event,False)
    time.sleep(5)
    print "state", dpfsm.fsm.current_state

    print "state", dpfsm.fsm.current_state
    event = events.mkevent("ActionConfirm")
    event.ev_dc['src_addr'] = 101
    event.ev_dc['dst_addr'] = 100
    event.ev_dc['peerlinkId'] = 0
    event_q.put(event,False)
    time.sleep(5)
    print "state", dpfsm.fsm.current_state
    
   
    
    
    
if __name__ == '__main__':
    try:
        test()
    except KeyboardInterrupt:
        pass



