#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Fri Dec  7 14:23:26 2012

@author: belza
'''



class NetworkConfiguration :
    ''' This class represents the actual network configuration'''
    def __init__(self, station_id, net_id, broadcast_addr, beacon_period=20, \
        number_of_peering=0, accepting_additional_peerings=True, max_retry=6, \
        retry_timeout=20, confirm_timeout=20, holding_timeout=40, \
        active_path_selection_protocol=1, active_path_selection_metric=1, \
        forwarding=True, TTL=31, active_congestion_control_mode=0, \
        active_syn_method=1, control_time=8,slots=8,list_nodes=None):
        '''  
        Constructor.
        
        802.11 management parameters
        @param station_id: MAC ADDRESS        
        @param net_id:  OCTET STRING, max 32
        @param broadcast_addr: MAC BROADCAST ADDRESS        
        @param beacon_period: INTEGER, number of time units (1024 microseconds) between beacons, DEFAULT = 40.       
        @param number_of_peering:  Unsigned32, indicates the number of mesh peering currently maintained by the STA,DEFAULT = 0.
        @param accepting_additional_peerings: TruthValue,indicates whether the station is willing to accept additional peerings, DEFAULT = True.
        @param max_retry: Unsigned32, specifies the maximum number of Peering Open retries that can be sent to establish a new  peering instance, DEFAULT = 2.
        @param retry_timeout: Unsigned32, specifies the initial retry timeout, in millisecond units, used by the Peering Open message, DEFAULT = 40.
        @param confirm_timeout: Unsigned32, specifies the initial confirm timeout, in millisecond units, used waiting for a Peering Confirm message, DEFAULT = 40.
        @param active_path_selection_protocol: INTEGER { hwmp (1), vendorSpecific (255) }, indicates the active path selection protocol, DEFAULT = 1.
        @param active_path_selection_metric: INTEGER { airtimeLinkMetric (1), vendorSpecific (255) }, indicates the active path selection metric, DEFAULT = 1.
        @param forwarding: TruthValue, specifies the ability of a mesh STA to forward MSDUs, DEFAULT = TRUE.
        @param TTL: Unsigned32, specifies the value of TTL subfield set at a source STA.DEFAULT = 31.
        @param active_congestion_control_mode: INTEGER {null(0), congestionControlSignaling (1), vendorSpecific (255) }, DEFAULT = 0.
        @param active_syn_method: INTEGER { neighborOffsetSynchronization (1), vendorSpecific (255) }, DEFAULT = 1.
        
        TDMA parameters, They are only necessary for the MASTER
        @param control_time: time between control frames 
        @param slots: number of slots
        @param list_nodes: array of mac addresses of nodes, in the order of the slots each of them will use.        
        
        '''
        self.station_id = station_id
        self.broadcast_addr = broadcast_addr
        self.net_id = net_id
        self.beacon_period = beacon_period
        self.number_of_peering = number_of_peering
        self.accepting_additional_peerings = accepting_additional_peerings 
        self.max_retry = max_retry
        self.retry_timeout = retry_timeout 
        self.confirm_timeout = confirm_timeout
        self.holding_timeout = holding_timeout
        self.active_path_selection_protocol = active_path_selection_protocol
        self.active_path_selection_metric = active_path_selection_metric
        self.forwarding = forwarding
        self.TTL = TTL
        self.active_congestion_control_mode = active_congestion_control_mode
        self.active_syn_method = active_syn_method
        "TDMA parameters"        
        self.control_time =control_time
        self.slots = slots
        self.list_nodes = list_nodes
        if self.list_nodes == None:
            self.list_nodes = []
            
        
        
    def setStationId(self,station_id):
         self.station_id = station_id
         
    def getStationId(self):
        return(self.station_id)
        
    def setBroadcastAddr(self,broadcast_addr):
         self.station_id = broadcast_addr
         
    def getBroadcastAddr(self):
        return(self.broadcast_addr)

    def setNetId(self,net_id):
         self.net_id = net_id
         
    def getNetId(self):
        return(self.net_id)
        
    def setBeaconPeriod(self,beacon_period):
         self.beacon_period = beacon_period
         
    def getBeaconPeriod(self):
        return(self.becon_period)

    def setNumberOfPeering(self,number_of_peering):
         self.number_of_peering = number_of_peering
         
    def getNumberOfPeering(self):
        return(self.number_of_peering)



def test():
    print ""
    
if __name__ == '__main__':
    try:
        test()
    except KeyboardInterrupt:
        pass


