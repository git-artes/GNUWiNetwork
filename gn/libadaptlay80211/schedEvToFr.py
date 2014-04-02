#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# schedEvToFr.py
#


'''An event to frame scheduler based on IEEE 802.11 frames.

A scheduler that gets an event from a Layer 2 input queue, generates the corresponding frame, and puts it into the Layer 1 transmit queue.
'''

import Queue
import sys
sys.path +=['..']

import libutils.gnscheduler as gnscheduler
import libevents.if_events as if_events



class SchedEvToFr(gnscheduler.Scheduler):
    '''Subclass of Scheduler for adapting Layers 1 and 2.
    '''

    def fn_sched(self):
        '''Scheduling function to process an events queue.
        
        Scheduling function to process an events queue: reads one element from the input event queue, generates a frame, and puts this frame in  the output queue.
        
        out_queues: a dictionary. 
        '''
        in_qu = self.in_queues[0]
        event = in_qu.get(True)
        
        frmobj = if_events.evtofrm(event)
        frame = frmobj.mkpkt()       

        out_queue = self.out_queues['frames']
        out_queue.put(frame, False)   # add to queue, don't block 
        #print "frame : ", repr(frame)
        in_qu.task_done()


if __name__ == '__main__':
    import doctest
    testfilename = sys.argv[0][:-2] + 'txt'
    try:
        doctest.testfile(testfilename)
    except:      # no text file present
        pass

