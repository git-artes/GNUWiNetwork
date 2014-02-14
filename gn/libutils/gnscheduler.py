#!/usr/bin/env python
# -*- coding: utf-8 -*-

# scheduler: a generic scheduler

'''Classes and Functions to implement a generic scheduler.

How to use:
  1. Create a subclass of Scheduler.
  2. Overwrite fn_sched() in the subclass.
  3. Write a test function to verify behavior.

In class C{Scheduler}, C{in_queues} and C{out_queues} may be any structure understood by C{fn_sched()}. This function C{fn_sched()} must get items from input queues, optionally do some work, and put items in output queues.

Examples of queue structures:
  - C{{name: queue}}, a dictionary of queues identified by name.
  - C{{priority:queue}}, a dictionary of queues by priority, 1<= priority <=10.
  - C{[queue]}, a list of queues, e.g. to put on the shortest, or to get from the longest.
  - C{{name: (function, queue)}}, a dictionary of tuples; name identifies queue, function is a task to perform specific to one queue. The function may even produce a different item to put in queue.
'''

import threading


class Scheduler(threading.Thread):
    '''Gets elements from input queues, processes, puts elements in output queues.
    
    This scheduler gets one element from one of several input queues, and puts elements in one or several output queues. Behaviour is regulated by a scheduling function which is expected to be overwritten when subclassing this class. Selection of input queue to get element from, processing, creation of one or more elements of same or different type, and putting elements in output queues are all regulated by this scheduling function.
    '''
 
    def __init__(self, in_queues, out_queues, debug=False):
        '''Constructor.
        
        @param in_queues: a list of input queues from which items are extracted. If input queues are given within a more elaborate structure, functin run() must be overwritten.
        @param out_queues: a structure containing the output queues. A possible structure is a dictionary of key nm_queue, the name of an output queue; value may be a queue, a tuple (function, queue) or other structure to be processed by the scheduling function fn_sched, which must be overwritten.
        @param debug: if True prints some debug messages; default False.
        '''
        if debug:
            print "inicializo"
        threading.Thread.__init__(self)
        self.daemon = True
        self.finished = False
        if type(in_queues) is list:        # accept a list of queues, or a single queue
            self.in_queues = in_queues
        else:
            self.in_queues = [in_queues]
        self.out_queues = out_queues    # output queues in a dictionary
        return

    def fn_sched(self):
        '''A dummy scheduling function; to be overwritten in a subclass.
        '''
        pass
        return


    def run(self, debug=False):
        '''Runs the scheduler until stopped.

        @param debug: if True prints some debug messages; default False.
        '''
        if debug:
            print "start .... run"
        while not self.finished:
            self.fn_sched()
        else:
            #print 'Scheduler, stopped'
            self.stop()
        for in_qu in self.in_queues:
            in_qu.join()
        return


    def stop(self, debug=False):
        '''Stops the scheduler.

        @param debug: if True prints some debug messages; default False.
        '''
        if debug:
            print 'Scheduler, in stop function'
        self.finished = True
        self._Thread__stop()



