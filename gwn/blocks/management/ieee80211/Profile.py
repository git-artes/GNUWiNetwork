#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Fri Dec  7 12:19:22 2012

@author: belza
'''



class Profile :
    ''' This class represents the profile of the network, in order to join the network the profile must be supported by all nodes.'''

    def __init__(self,net_id,path_selection_protocol=1, \
        path_selection_metric=1, congestion_control_mode=0, syn_method=1, \
        authentication_protocol=0 ):
        '''Constructor.
        
        @param net_id: A Mesh ID, String, length max 32.
        @param path_selection_protocol: A path selection protocol identifier,  INTEGER \{ hwmp (1), vendorSpecific (255)\},DEFAULT = 1.  
        @param path_selection_metric: A path selection metric identifier,INTEGER\{ airtimeLinkMetric (1), vendorSpecific (255) \},DEFAULT = 1.
        @param congestion_control_mode: A congestion control mode identifier, INTEGER \{null (0),congestionControlSignaling (1), vendorSpecific (255) \},DEFAULT =0.
        @param syn_method: A synchronization method identifier, INTEGER \{neighborOffsetSynchronization (1),vendorSpecific (255) \}, DEFAULT =1.
        @param authentication_protocol:  An authentication protocol identifier, INTEGER \{null (0), sae (1), ieee8021x (2),vendorSpecific (255) \}, DEFAULT = 0.
        '''        
        self.net_id = net_id
        self.path_selection_protocol = path_selection_protocol
        self.path_selection_metric = path_selection_metric 
        self.congestion_control_mode = congestion_control_mode
        self.syn_method = syn_method
        self.authentication_protocol = authentication_protocol
        
        
    def __eq__(self, other):
        if isinstance(other, Profile):
            if self.net_id == other.net_id and \
                self.authentication_protocol == other.authentication_protocol and \
                self.congestion_control_mode == other.congestion_control_mode and \
                self.path_selection_metric == other.path_selection_metric and \
                self.path_selection_protocol == other.path_selection_protocol and \
                self.syn_method == other.syn_method:
                return True
        return NotImplemented


    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result    


    def setAuthenticationProtocol(self,protocol):
        self.authentication_protocol=protocol



def test():
    pass
    
if __name__ == '__main__':
    try:
        test()
    except KeyboardInterrupt:
        pass
