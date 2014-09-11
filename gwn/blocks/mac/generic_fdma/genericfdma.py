#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
A generic FDMA block.
'''

import sys, threading
#sys.path +=sys.path + ['..']

import gwnblocks.gwnblock as gwn



class GenericFDMA(gwn.GWNBlock):
    '''A simple FDMA.
    '''

    #def __init__(self,bandDL1,bandUL1):
    def __init__(self):
        '''Constructor.
        '''        
        super(GenericFDMA, self).__init__(1, 'GenericFDMA', 2, 2)
        self.finished = False
        

    def process_data(self, port_type, port_nr, ev):
        '''Generic FDMA process.
        '''
        if port_nr == 0:
            self.write_out(0, ev)
        elif port_nr == 1:
            self.write_out(1, ev)
        else:
            pass # raise a reasonable exception
        return


