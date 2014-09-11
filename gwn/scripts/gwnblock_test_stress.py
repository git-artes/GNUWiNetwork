#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Tests how many threads can be opened.

Created on Thu Dec 13 14:31:45 2012
@author: belza
'''

import threading,Queue
import sys
sys.path +=sys.path + ['..']

class gwnBlock(threading.Thread):
    '''The main block. All blocks inherit from it.
    '''

    def __init__(self, number_in=0,number_out=0,number=0):
        '''  
        Constructor.
        
        @param number_in: the number of input ports of this block.
        @param number_out: the number of output ports of this block.
        '''        
        threading.Thread.__init__(self)
        self.ports_in = None
        self.ports_out =None
        self.finished = False
        self.set_in_size(number_in)
        self.set_out_size(number_out)
        self.number = number

    def run(self):
        while 1:
           aux = self.ports_in[0].get()
           print aux,self.number
           
    def set_in_size(self,number_in):
        '''Creates a list of input connections.

        Creates a list of empty items; each of the empty items will be later replaced by a list acting as an input connection.
        @param number_in: the number of input connections.
        '''
        self.ports_in = number_in*[None]

    def set_out_size(self,number_out):
        '''Creates a list of output connections.

        Creates a lists of empty lists; each of the empty lists is an output connection.
        @param number_out: the number of output connections.
        '''
        self.ports_out = [[] for x in xrange(number_out)]

    def get_port_in(self,index):
        '''Returns an input list to this block.

        Returns the input list to this block placed in the position indicated by index.
        @param index: the position of the input list to return.
        '''
        return self.ports_in[index]

    def set_connection_in(self,connector,index):
        '''Sets an input connection to this block.

        The connector, a list, is assigned as an input connection to this block in the position indicated by index.
        @param connector: a reference to a list.
        @param index: a position in ports_in.
        '''
        if index <= len(self.ports_in)-1:
            self.ports_in[index] = connector

    def set_connection_out(self,connector,index):
        '''Sets an ouput connection to this block.

        The connector, a list, is assigned as an output connection to this block in the position indicated by index.
        @param connector: a reference to a list.
        @param index: a position in ports_in.
        '''
        if index <= len(self.ports_out)-1:
            self.ports_out[index].append(connector)
    
    def stop(self):
            self.finished = True
            self._Thread__stop()

def test():
    '''A test function.
    '''
    
    myQueue=Queue.Queue(10)
    myQueue1=400*[None]
    gwnblock=400*[None]
    i=1
    while i<375:
        gwnblock[i] =gwnBlock(5,7,i)
        myQueue1[i]=Queue.Queue(10)
        gwnblock[i].set_connection_in(myQueue1[i],0)
        gwnblock[i].set_connection_in(myQueue,3)
        myQueue1[i].put("hola")
        gwnblock[i].start()
        i=i+1
    myQueue1[20].put("chau")
    gwnblock[1].join()
#    gwnblock.set_connection_out(myQueue,2)
#    gwnblock.ports_out[2].put("hola")
#    print gwnblock.ports_out   
#    print gwnblock.ports_out[2].get()
#    gwnblock.set_connection_out(myQueue,9)
 
    

if __name__ == '__main__':
    try:
        test()
    except KeyboardInterrupt:
        pass


