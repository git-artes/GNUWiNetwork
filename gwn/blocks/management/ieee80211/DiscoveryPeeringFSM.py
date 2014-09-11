#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Tue May  7 12:42:54 2013

@author: belza
'''

import sys
sys.path +=['..']

import Queue,time,threading

import utils.libfsm.fsm as fsm
import gwnevents.api_events as events
import blocks.utilblocks.timer.timer as Timer
import NetworkConfiguration



class DiscoveryPeeringFSM() :
    '''The discovery and peering finite state machine.
    
    This class implements the  state machine for Discovery and Peering (IEEE  Std 802.11-2012 pg 1365).
    '''

    def __init__(self,link_id,network_conf,tx_event_q,event_q,peer_addr):
        '''  
        Constructor.
        
        @param link_id: each state machine is associated with a network link. This is the identification of the link or the state machine.
        @param network_conf: actual network configuration.        
        @param tx_event_q: The event queue where to put the new events.
        @param event_q: The event queue of the fsm controller. Will be passed to the Timers in order to generates Timer events to the fsm controller
        '''

        self.tx_event_q = tx_event_q
        self.event_q = event_q
        self.net_conf = network_conf
        self.link_id = link_id
        self.peer_addr = peer_addr
        self.timerRetry = None
        self.timerHolding =None
        self.timerConfirm =None

        self.fsm = fsm.FSM ('IDLE', []) # "memory" will be used as a stack.
        #self.fsm.set_default_transition (self.Error, 'IDLE')
        self.fsm.add_transition_any  ('IDLE', None, 'IDLE')
        self.fsm.add_transition_any  ('OPN_SNT', None, 'OPN_SNT')        
        self.fsm.add_transition_any  ('CNF_RCVD', None, 'CNF_RCVD')
        self.fsm.add_transition_any  ('OPN_RCVD', None, 'OPN_RCVD')        
        self.fsm.add_transition_any  ('ESTAB', None, 'ESTAB')
        self.fsm.add_transition_any  ('HOLDING', None, 'HOLDING')        
        
   
        
        # ------------------ Transitions from IDLE ----------------------------
        self.fsm.add_transition ('REQ_RJCT', 'IDLE', self.sndCLS, 'IDLE')
        self.fsm.add_transition ('ACTOPN', 'IDLE', self.sndOPNsetR, 'OPN_SNT')
        self.fsm.add_transition ('OPN_ACPT', 'IDLE', self.sndCNFsetR, 'OPN_RCVD')
    
        # ------------------ Transitions from OPN_SNT -------------------------
        # --- remark: when arrives TOR1 arrives and the state is OPN_SNT I will not setR as in the standar because is considered in the implementation of the Timer" 
        self.fsm.add_transition ('TOR1', 'OPN_SNT', self.sndOPN, 'OPN_SNT') 
        self.fsm.add_transition ('CNF_ACPT', 'OPN_SNT', self.clRsetC,  'CNF_RCVD')
        self.fsm.add_transition ('OPN_ACPT', 'OPN_SNT', self.sndCNF,  'OPN_RCVD')
        self.fsm.add_transition_list (['CLS_ACPT', 'OPN_RJCT', 'CNF_RJCT', 'TOR2', 'CNCL'], 'OPN_SNT', self.sndCLSclRsetH, 'HOLDING')
        
        # ------------------ Transitions from CNF_RCVD ------------------------
        self.fsm.add_transition ('OPN_ACPT', 'CNF_RCVD', self.clCsndCNF, 'ESTAB')
        self.fsm.add_transition_list (['CLS_ACPT', 'OPN_RJCT', 'CNF_RJCT', 'CNCL'], 'CNF_RCVD', self.sndCLSclCsetH,   'HOLDING')
        self.fsm.add_transition      ('TOC',   'CNF_RCVD',    self.sndCLSsetH,   'HOLDING')
    
        # ------------------ Transitions from OPN_RCVD ------------------------
        # --- remark: when arrives TOR1 and the state is OPN_RCVD we will not call setR as in the standar because is not necesseray with our  implementation of the Timer class" 

        self.fsm.add_transition      ('OPN_ACPT',               'OPN_RCVD',         self.sndCNF,              'OPN_RCVD')
        self.fsm.add_transition      ('TOR1',                   'OPN_RCVD',         self.sndOPN,          'OPN_RCVD')
        self.fsm.add_transition      ('CNF_ACPT',               'OPN_RCVD',         self.clR,                 'ESTAB')
        self.fsm.add_transition_list      (['CLS_ACPT', 'OPN_RJCT', 'CNF_RJCT', 'TOR2', 'CNCL'],   'OPN_RCVD',      self.sndCLSclRsetH,   'HOLDING')    
        
        # ------------------ Transitions from ESTAB ---------------------------
        self.fsm.add_transition      ('OPN_ACPT',               'ESTAB',         self.sndCNF,              'ESTAB')
        self.fsm.add_transition_list      (['CLS_ACPT', 'OPN_RJCT', 'CNF_RJCT', 'CNCL'],   'ESTAB',     self.sndCLSsetH,   'HOLDING')
    
        # ------------------ Transitions from HOLDING -------------------------
        self.fsm.add_transition      ('TOH',               'HOLDING',         None,              'IDLE')
        self.fsm.add_transition      ('CLS_ACPT',          'HOLDING',         self.clH,               'IDLE')
        self.fsm.add_transition_list      (['OPN_ACPT','CNF_ACPT', 'OPN_RJCT', 'CNF_RJCT', 'CNCL'],   'HOLDING',     self.sndCLS,   'HOLDING')
        
    def appendToMemory(self,data):    
        self.fsm.memory.append (data) 
        
    def sndCLS(self,fsm):
        event = events.mkevent("ActionClose")
        event.ev_dc['src_addr'] = self.net_conf.station_id
        event.ev_dc['dst_addr']= self.peer_addr
        event.ev_dc['peerlinkId'] = self.link_id
        self.tx_event_q.put(event,False)
    
    def sndOPN(self,fsm):
        event = events.mkevent("ActionOpen")
        event.ev_dc['src_addr'] = self.net_conf.station_id
        event.ev_dc['dst_addr'] = self.peer_addr
        event.ev_dc['peerlinkId'] = self.link_id
        self.tx_event_q.put(event,False)

    def sndCNF(self,fsm):
        event = events.mkevent("ActionConfirm")
        event.ev_dc['src_addr'] =self.net_conf.station_id
        event.ev_dc['dst_addr'] = self.peer_addr
        event.ev_dc['peerlinkId'] = self.link_id
        self.tx_event_q.put(event,False)

    def setR(self,fsm):
        self.timerRetry=Timer.Timer(self.event_q,self.net_conf.retry_timeout,self.net_conf.max_retry,"TimerTOR1", self.link_id,"TimerTOR2" )
        self.timerRetry.start()
        
    def setC(self,fsm):
        self.timerConfirm=Timer.Timer(self.event_q,self.net_conf.confirm_timeout,1,"TimerTOC", self.link_id )
        self.timerConfirm.start()
        
    def setH(self,fsm):
        self.timerHolding=Timer.Timer(self.event_q,self.net_conf.holding_timeout,1,"TimerTOH", self.link_id )
        self.timerHolding.start()

    def clH(self,fsm):
       self.timerHolding.stop()
       print "STOP HOLDING TIMER"
 
    def clR(self,fsm):
       self.timerRetry.stop()
       print "STOP RETRY TIMER"
      

    def clC(self,fsm):
       self.timerConfirm.stop()
       print "STOP CONFIRM TIMER"

    def sndOPNsetR(self,fsm):
        self.sndOPN(fsm)
        self.setR(fsm)

    def sndCNFsetR(self,fsm):
        self.sndCNF(fsm)
        self.setR(fsm)
        
    def clRsetC(self,fsm):
        self.clR(fsm)
        self.setC(fsm)
        
    def sndCLSclRsetH(self,fsm):
        self.sndCLS(fsm)
        self.clR(fsm)
        self.setH(fsm)

    def clCsndCNF(self,fsm):
        self.clC(fsm)
        self.sndCNF(fsm)
        
    def sndCLSclCsetH(self,fsm):
        self.sndCLS(fsm)
        self.clC(fsm)
        self.setH(fsm)
        
    def sndCLSsetH(self,fsm):
        self.sndCLS(fsm)
        self.setH(fsm)


    def Error (self,fsm):
        print 'That does not compute the state machine.'
        print str(fsm.input_symbol)



def test():
    tx_event_q=Queue.Queue(10)
    event_q=Queue.Queue(10)
    net_conf1 = NetworkConfiguration.NetworkConfiguration(100,'my network',256,1)
    net_conf1.retry_timeout = 5
    mydpfsm = DiscoveryPeeringFSM(127, net_conf1,tx_event_q,event_q,101)
    read_tx = ReadQueueTxEmulator(tx_event_q)
    read_tx.start()
    read_ev_q = ControllerFsmEmulator(event_q,mydpfsm.fsm)
    read_ev_q.start() 
    
    # ---------------------------------------------------------------------
    # TEST 1: ON IDLE RECEIVE A REQ_RJCT EVENT, SEND A CLOSE AND STAY ON IDLE
    print ""
    print " START TEST 1 --------------------------------------------" 
    print "STATE BEFORE PROCESS REQ_REJCT ", mydpfsm.fsm.current_state
    mydpfsm.fsm.process("REQ_RJCT")    
    print "STATE AFTER PROCESS REQ_REJCT ", mydpfsm.fsm.current_state
    print ""    

    # ---------------------------------------------------------------------
    # TEST 2: ON IDLE RECEIVE A ACTOPN, SEND CONFIRM, MOVES TO STATE OPN_SNT, START TOR1 (5s)
    # RETRY TOR1 3 TIMES, after each TOR1, send CONFIRM, arrives TOR2,send CLOSE, moves to STATE HOLDING
    # ARRIVES TOH and go to IDLE state, wait this thread during 60 seconds to end all this process
    print ""
    print " START TEST 2 --------------------------------------------" 
    net_conf1.retry_timeout = 5
    net_conf1.max_retry = 3
    print "STATE BEFORE PROCESS ACTOPN ", mydpfsm.fsm.current_state     
    mydpfsm.fsm.process("ACTOPN")    
    print "STATE AFTER PROCESS ACTOPN ", mydpfsm.fsm.current_state
    time.sleep(60)
    print ""    

    # ---------------------------------------------------------------------
    # TEST 3: ON IDLE RECEIVE A OPN_ACPT, SEND CONFIRM, MOVES TO STATE OPN_RCVD, START TOR1 (5s)
    # RETRY TOR1 3 TIMES, after each TOR1, send CONFIRM, arrives TOR2,send CLOSE, moves to STATE HOLDING
    # ARRIVES TOH and go to IDLE state, wait this thread during 60 seconds to end all this process
    net_conf1.retry_timeout = 5
    net_conf1.max_retry = 3
    print ""
    print " START TEST 3 --------------------------------------------" 
    print "STATE BEFORE PROCESS OPN_ACPT ", mydpfsm.fsm.current_state     
    mydpfsm.fsm.process("OPN_ACPT")    
    print "STATE AFTER PROCESS OPN_ACPT ", mydpfsm.fsm.current_state
    time.sleep(60)
    print ""

    # ---------------------------------------------------------------------
    # TEST4: Initial state IDLE and receives an ACTOPN, SEND CONFIRM, MOVES TO STATE OPN_SNT, START TOR1 (5s)
    # AFTER THAT, RECEIVES A OPN_ACPT, send CONFIRM, moves to OPN_RCVD, RETRY TOR1 3 TIMES, after each TOR1, send CONFIRM, arrives TOR2,send CLOSE, moves to STATE HOLDING
    # ARRIVES TOH and go to IDLE state, wait this thread during 60 seconds to end all this process
    print ""
    print " START TEST 4 --------------------------------------------" 
    net_conf1.retry_timeout = 5
    net_conf1.max_retry = 3
    print "STATE BEFORE PROCESS ACTOPN ", mydpfsm.fsm.current_state     
    mydpfsm.fsm.process("ACTOPN")    
    print "STATE AFTER PROCESS ACTOPN ", mydpfsm.fsm.current_state
    time.sleep(1)
    mydpfsm.fsm.process("OPN_ACPT")    
    print "STATE AFTER PROCESS OPN_ACPT ", mydpfsm.fsm.current_state
    time.sleep(60)
    print ""
    
    # ---------------------------------------------------------------------
    # TEST 5: Initial state IDLE and receives an ACTOPN, SEND CONFIRM, MOVES TO STATE OPN_SNT, START TOR1 (5s)
    # AFTER THAT, RECEIVES A CNF_ACPT, Clear Retry timer, Set Confirm timer, Moves to CNF_RCVD, Recieves a TOC, send CLOSE, MOVES TO HOLDING, set Holding Timer
    # ARRIVES TOH and go to IDLE state, wait this thread during 100 seconds to end all this process
    print ""
    print " START TEST 5 --------------------------------------------" 
    net_conf1.retry_timeout = 5
    net_conf1.max_retry = 3
    print "STATE BEFORE PROCESS ACTOPN ", mydpfsm.fsm.current_state     
    mydpfsm.fsm.process("ACTOPN")    
    print "STATE AFTER PROCESS ACTOPN ", mydpfsm.fsm.current_state
    time.sleep(1)
    mydpfsm.fsm.process("CNF_ACPT")    
    print "STATE AFTER PROCESS CNF_ACPT ", mydpfsm.fsm.current_state
    time.sleep(100)
    print ""

    # ---------------------------------------------------------------------
    # TEST 6: Initial state IDLE receives an ACTOPN, SEND CONFIRM, MOVES TO STATE OPN_SNT, START TOR1 (5s)
    # AFTER THAT, RECEIVES A CNF_ACPT, Clear Retry timer, Set Confirm timer, Moves to CNF_RCVD, Receives OPN_ACPT, send CONFIRM, MOVES TO ESTAB
    # ARRIVES CLS_ACPT send Close set Holding Timer moves to HOLDING. TOH srrives and go to IDLE state, wait this thread during 100 seconds to end all this process
    print ""
    print " START TEST 6 --------------------------------------------" 
    net_conf1.retry_timeout = 5
    net_conf1.max_retry = 3
    print "STATE BEFORE PROCESS ACTOPN ", mydpfsm.fsm.current_state     
    mydpfsm.fsm.process("ACTOPN")    
    print "STATE AFTER PROCESS ACTOPN ", mydpfsm.fsm.current_state
    time.sleep(1)
    mydpfsm.fsm.process("CNF_ACPT")    
    print "STATE AFTER PROCESS CNF_ACPT ", mydpfsm.fsm.current_state
    time.sleep(1)
    mydpfsm.fsm.process("OPN_ACPT")    
    print "STATE AFTER PROCESS OPN_ACPT ", mydpfsm.fsm.current_state
    time.sleep(5)
    mydpfsm.fsm.process("CLS_ACPT")    
    print "STATE AFTER PROCESS CLS_ACPT ", mydpfsm.fsm.current_state

    # ---------------------------------------------------------------------
    # TEST 7: Initial state IDLE receives an OPN_ACPT, SEND CONFIRM, MOVES TO STATE OPN_RCVD, START TOR1 (5s)
    # AFTER THAT, RECEIVES A CNF_ACPT, Clear Retry timer, MOVES TO ESTAB
    # ARRIVES CLS_ACPT send Close set Holding Timer moves to HOLDING. TOH srrives and go to IDLE state, wait this thread during 100 seconds to end all this process
    print ""
    print " START TEST 7 --------------------------------------------" 
    net_conf1.retry_timeout = 5
    net_conf1.max_retry = 3
    print "STATE BEFORE PROCESS ACTOPN ", mydpfsm.fsm.current_state     
    mydpfsm.fsm.process("OPN_ACPT")    
    print "STATE AFTER PROCESS OPN_ACPT ", mydpfsm.fsm.current_state
    time.sleep(1)
    mydpfsm.fsm.process("CNF_ACPT")    
    print "STATE AFTER PROCESS CNF_ACPT ", mydpfsm.fsm.current_state
    time.sleep(5)
    mydpfsm.fsm.process("CLS_ACPT")    
    print "STATE AFTER PROCESS CLS_ACPT ", mydpfsm.fsm.current_state
    time.sleep(100)
    print ""
            
    if read_ev_q.isAlive():        
        read_ev_q.stop()
    if read_tx.isAlive():
        read_tx.stop()
    print "FIN"       



        
class ReadQueueTxEmulator(threading.Thread) :
 
    def __init__(self,tx_event_q):
        threading.Thread.__init__(self)
        self.tx_event_q = tx_event_q
        self.finished = False
        
    def run(self):
        while not self.finished:
            event= self.tx_event_q.get()        
            print " event transmited ", event, " ", int(round(time.time() * 1000)) 
            
    def stop(self):
        print "STOP Tx Emulator CALLED"
        self.finished = True
        print "SET DONE"
        self._Thread__stop()


                        
class ControllerFsmEmulator(threading.Thread) :
 
    def __init__(self,event_q,fsm):
        threading.Thread.__init__(self)
        self.event_q = event_q
        self.fsm = fsm
        self.finished = False
    
    def run(self):
        while not self.finished:
            event= self.event_q.get()
            print " event arrives at the fsm controller ", event, " ", \
                event.ev_dc['add_info'], int(round(time.time() * 1000)) 
            print "estado antes de procesar este evento ", \
                self.fsm.current_state
            self.fsm.process(event.ev_subtype) 
            print "estado luego de procesar este evento ", \
                self.fsm.current_state
            
    def stop(self):
        print "STOP Controller Fsm Emulator CALLED"
        self.finished = True
        print "SET DONE"
        self._Thread__stop()



if __name__ == '__main__':
    try:
        test()
    except KeyboardInterrupt:
        pass



