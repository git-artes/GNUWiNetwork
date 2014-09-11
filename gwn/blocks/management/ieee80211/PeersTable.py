#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Tue Dec 11 14:40:05 2012

@author: belza
'''

import sys
sys.path +=['..']
import Queue
import NetworkConfiguration
import DiscoveryPeeringFSM
from operator import itemgetter



class PeersTable :
    
    '''This class maintain the active peer links list.
    
    Each item of the list has the following elements: the peer MAC address, the local link Id, the peer Link Id and the corresponding state machine (object) of the PMP protocol.
    '''

    def __init__(self):
        '''Constructor: build an empty list.
        '''
        self.my_list=[]
  
    def add(self,peerMACaddr, event_q,tx_frame_q,net_conf, localLinkId, \
        peerLinkId=0):
        '''Create state machine SMDiscoveryPeering and new item in peers list.
        
        @param tx_frame_q: the events transmition queue, it is necessary as a reference for the state machine.
        @param peerMACaddr: The MAC address of the peer.
        @param localLinkId: My link Id.
        @param peerLinkId: The link Id of my peer. DEFAULT = 0.
        '''
        self.my_addr = net_conf. getStationId()
        sm = DiscoveryPeeringFSM.DiscoveryPeeringFSM(localLinkId, \
            net_conf,tx_frame_q,event_q,peerMACaddr) 
        self.my_list.append({'peerMac':peerMACaddr,'localLinkId': localLinkId, \
            'peerLinkId': peerLinkId,'state_machine':sm})

    def getIndex(self,peerMACaddr=None,localLinkId=None):
        ''' Given the peer MAC Address return the index in the list of peers.
        '''
        if peerMACaddr:
            return map(itemgetter('peerMac'), self.my_list).index(peerMACaddr)
        if localLinkId:
            return map(itemgetter('localLinkId'), self.my_list).index(localLinkId)
            
        
    def delete(self,peerMACaddr):
        ''' Delete the register of the peers list of the given MAC address.
        '''
        if self.isMember(peerMACaddr):
            self.my_list.__delitem__(self.getIndex(peerMACaddr))


    def updatePeerLinkId(self,peerMACaddr,peerLinkId):
        '''Update peer link ID for given MAC address in peers list.

        If there exists a register in the peers list for the given MAC address update the peer link Id element.
        '''
        if self.isMember(peerMACaddr = peerMACaddr):
            self.my_list[self.getIndex(peerMACaddr)]['peerLinkId']=peerLinkId

    def isMember(self,peerMACaddr=None,localLinkId=None):

        if peerMACaddr:
            return map(itemgetter('peerMac'), \
                self.my_list).__contains__(peerMACaddr)
        if localLinkId:
            return map(itemgetter('localLinkId'), \
                self.my_list).__contains__(localLinkId)
            
    def getSM(self,peerMACaddr=None, localLinkId=None):
        '''Return state machine object for given MAC address.
        
        If there exsits a register in the peers list for the given MAC address gives the corresponding state machine object.
        '''
        if peerMACaddr:
            if self.isMember(peerMACaddr = peerMACaddr):        
                return  self.my_list[self.getIndex(peerMACaddr = peerMACaddr)]\
                   ['state_machine']
        if localLinkId:
            if self.isMember(localLinkId = localLinkId):        
                return  self.my_list[self.getIndex(localLinkId = localLinkId)]\
                    ['state_machine']

    def getLocalLinkId(self,peerMACaddr):
        if self.isMember(peerMACaddr =peerMACaddr):        
            return  self.my_list[self.getIndex(peerMACaddr = peerMACaddr)]\
                ['localLinkId']

    def getPeerLinkId(self,peerMACaddr):
        if self.isMember(peerMACaddr = peerMACaddr):        
            return  self.my_list[self.getIndex(peerMACaddr = peerMACaddr)]\
                ['peerLinkId']
    
    
    def printPeersTable(self):
        '''Print the peers table.
        '''
        print self.my_addr, " PEERS TABLE: peerMAC,local link Id, Peer link Id, state \n"
        for i in range(0,len(self.my_list)):
            #print "Register number :", i, '\n'
            print self.my_list[i]['peerMac'],  self.my_list[i]['localLinkId'],\
                self.my_list[i]['peerLinkId'],self.my_list[i]['state_machine'].\
                fsm.current_state, '\n'      


def test():
    event_q = Queue.Queue(10)
    tx_frame_q = Queue.Queue(10)
    net_conf1 = NetworkConfiguration.NetworkConfiguration(100,'my network',256,1)    
    localLinkId =10
    peerLinkId=0    
    
    p=PeersTable()
    p.add(255, event_q,tx_frame_q,net_conf1,localLinkId,peerLinkId)
    p.add(257, event_q,tx_frame_q,net_conf1,localLinkId+1,peerLinkId)
    p.printPeersTable()
    print "Index : ", p.getIndex(255)
    p.updatePeerLinkId(255, 13)
    print "Nuevo Peer link Id : ", p.getPeerLinkId(255)
    p.updatePeerLinkId(258, 14)
    print "Nuevo Peer link Id : ", p.getPeerLinkId(255)
    print "Id of the state machine : ", p.getSM(localLinkId=11).link_id
    p.delete(257)
    p.printPeersTable()
    p.delete(255)
    p.printPeersTable()
    p.delete(257)
    
    


if __name__ == '__main__':
    try:
        test()
    except KeyboardInterrupt:
        pass
