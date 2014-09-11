#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    This file is part of GNUWiNetwork,
#    Copyright (C) 2014 by 
#        Pablo Belzarena, Gabriel Gomez Sena, Victor Gonzalez Barbone,
#        Facultad de Ingenieria, Universidad de la Republica, Uruguay.
#
#    GNUWiNetwork is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GNUWiNetwork is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GNUWiNetwork.  If not, see <http://www.gnu.org/licenses/>.
#

'''
IEEE 802.11 CSMA MAC
'''

import sys
import time

sys.path += sys.path + ['..']
import gwnevents.api_events as events
import gwnblocks.gwnblock as gwn
import gwnblocks.gwninport as inport
import utils.logger.gnlogger as gnlogger
import logging
module_logger = logging.getLogger(__name__)
import utils.libfsm.fsm as fsm
import blocks.management.ieee80211.NetworkConfiguration as nc
import random

Loses = 0
aSIFSTime = 1
aDIFSTime = 1
# "CTS_Time” shall be calculated using the length of the CTS frame and the data rate at which the RTS frame used for the most recent NAV update was received.
CTS_Time = 14*8/34000  # 14 bytes, 34M ??
aSlotTime = 10
aRTSThreshold = 60
aPHY_RX_START_Delay = 1
dot11LongRetryLimit = 5
dot11ShortRetryLimit = 5
CWmin = 15
CWmax = 1023
CTSTout = aSIFSTime + aSlotTime + aPHY_RX_START_Delay
ACKTout = aSIFSTime + aSlotTime + aPHY_RX_START_Delay

class IEEE80211(gwn.GWNBlock):
    '''A CSMA IEEE 802.11 MAC implementation

    This class is a 802.11 mac implementation.
    Receives events from Layer 3 and Layer 1 and generates Control Frames.
    Some timers are needed.
    '''

    def __init__(self, nodeid):
        '''Constructor.
        
        @param 

        inport 0: events from L1
        inport 1: events from L3
        outport 0: events to L1
        outport 1: events to L3
        timer 0: wait for CTS
        timer 1: wait for Data ACK
        ......................
        '''        
        super(IEEE80211,self).__init__(1, "IEEE80211_1", 2, 2, 2)

        self.nodeid = nodeid
        #self.logger = logging.getLogger(str(self.__class__))
        self.logger = module_logger
        gnlogger.logconf()         # initializes the logging facility
        self.logger.info(str(self.nodeid) + ' start')

        self.initvars()

        self.net_conf = nc.NetworkConfiguration(self.nodeid,'my network',256,1)

        self.macfsm = fsm.FSM ('IDLE', []) 
        self.initmacfsm()
        
    def initvars(self):
        self.LRC = 0 # Long Retry Counter
        self.SRC = 0 # Short Retry Counter
        self.NAV = 0 # Network Allocation Vector
        self.PAV = 0 # Physical Allocation Vector
        self.BC = 0 # Backoff
        self.CW = CWmin # Current Window
        self.datatosend = 0

    def initmacfsm(self):
        self.macfsm.set_default_transition (self.Error, 'IDLE')

        self.macfsm.add_transition      ('L3Data',    'IDLE',       self.rcvL3,    'WAIT_ACK'  )
        self.macfsm.add_transition      ('Beacon',    'IDLE',       self.rcvL3,    'WAIT_ACK'  )
        self.macfsm.add_transition      ('L1Data',    'IDLE',       self.rcvL1,    'IDLE'      )
        self.macfsm.add_transition      ('RTS',       'IDLE',       self.rcvRTS,   'IDLE'      )
        self.macfsm.add_transition      ('CTS',       'IDLE',       self.updNAV,   'IDLE'      )
        self.macfsm.add_transition_any  (             'IDLE',       self.Error,    'IDLE'      )

        self.macfsm.add_transition      ('ACK',       'WAIT_ACK',   self.rcvACK,   'IDLE'      )
        self.macfsm.add_transition      ('ACKTout',   'WAIT_ACK',   self.sndData,  'WAIT_ACK'  )
        self.macfsm.add_transition      ('DataAbort', 'WAIT_ACK',   self.sndData,  'IDLE'      )
        self.macfsm.add_transition      ('RTS',       'WAIT_ACK',   self.rcvRTS,   'WAIT_CTS'  )
        self.macfsm.add_transition_any  (             'WAIT_ACK',   self.Error,    'WAIT_ACK'  )

        self.macfsm.add_transition      ('CTS',       'WAIT_CTS',   self.sndData,  'WAIT_ACK'  )
        self.macfsm.add_transition      ('CTSTout',   'WAIT_CTS',   self.sndRTS,   'WAIT_CTS'  )
        self.macfsm.add_transition      ('RTSAbort',  'WAIT_CTS',   self.sndRTS,   'IDLE'      )
        self.macfsm.add_transition      ('RTS',       'WAIT_CTS',   self.rcvRTS,   'WAIT_CTS'  )
        self.macfsm.add_transition_any  (             'WAIT_CTS',   self.Error,    'WAIT_CTS'  )

    def process_data(self, port_type, port_nr, ev):
        '''
        '''

        tag = ev.ev_subtype
        if port_type == "intimer":
            self.logger.debug(str(self.nodeid) + ' Timer event arrives at the fsm controller')
        elif port_type == "inport":
            if ev.ev_subtype == "Data":
                if port_nr == 0:        # from L1
                    self.logger.debug(str(self.nodeid) + ' L1 data event arrives at the fsm controller')
                    tag = 'L1' + ev.ev_subtype
                elif port_nr == 1:        # from L3
                    self.logger.debug(str(self.nodeid) + ' L3 data event arrives at the fsm controller')
                    tag = 'L3' + ev.ev_subtype
                else:
                    self.logger.debug(str(self.nodeid) + ' Received event %s in port %s %d:' % (ev, port_type, port_nr))
                    return
            else:
                self.logger.debug(str(self.nodeid) + ' Lx control or management data event arrives')
        else:
            self.logger.debug(str(self.nodeid) + ' Received event %s in port %s %d:' % (ev, port_type, port_nr))
            return

        self.macfsm.memory = ev
        self.macfsm.process(tag)

        '''
    def set_config(self, event):
        if 'interval' in event.ev_dc:
            self.interval = event.ev_dc['interval']
        if 'retry' in event.ev_dc:
            self.retry = event.ev_dc['retry']
        if 'nickname1' in event.ev_dc:
            self.nickname1 = event.ev_dc['nickname1']
        if 'nickname2' in event.ev_dc:
            self.nickname2 = event.ev_dc['nickname2']
        else:
            self.nickname2 = None
        if 'add_info' in event.ev_dc:
            self.add_info = event.ev_dc['add_info']
        else:
            self.add_info = None
        '''

    def Error(self, fsm):
        self.logger.error(str(self.nodeid) + ' Default transition for symbol: '+ str(fsm.input_symbol) + ", state: " + str(fsm.current_state))
        return True

    def rcvL3(self, fsm):
        self.logger.info(str(self.nodeid) + ' Receive from L3')
        event = self.macfsm.memory
        self.datatosend = self.macfsm.memory
        if (event.ev_dc['frame_length'] > aRTSThreshold):
            self.sndRTS(fsm)
            self.logger.debug(str(self.nodeid) + ' start timer')
            self.set_timer(0, interrupt=True)
            self.set_timer(0, False, CTSTout, dot11ShortRetryLimit, 'TimerCTSTout', None, 'TimerRTSAbort')
            self.macfsm.next_state = 'WAIT_CTS'
        else:
            self.sndData(fsm)
            self.logger.debug(str(self.nodeid) + ' start timer')
            if (self.datatosend.ev_dc['frame_length'] > aRTSThreshold):
                retrylimit = dot11ShortRetryLimit
            else:
                retrylimit = dot11LongRetryLimit
            self.set_timer(1, interrupt=True)
            self.set_timer(1, False, ACKTout, retrylimit, 'TimerACKTout', None, 'TimerDataAbort')
        return True

    def sndData(self, fsm):
        event = self.macfsm.memory
        if (event.ev_subtype == 'ACKTout'):
            if (event.nickname == 'TimerDataAbort'):
                self.logger.debug(str(self.nodeid) + ' Send Data EXAUSTED')
                self.discard()
                self.CW = CWmin
                self.SRC = 0
                self.LRC = 0
                self.set_timer(1, interrupt=True)
                return False
            elif (event.nickname == 'TimerACKTout'):
                self.logger.debug(str(self.nodeid) + ' Send Data. Retry')
                self.datatosend.ev_dc['retry'] = 1;
                if (event.ev_dc['frame_length'] > aRTSThreshold):
                    self.LRC += 1
                    if (self.LRC >= dot11LongRetryLimit):
                        self.discard()
                        self.set_timer(1, interrupt=True)
                        self.CW = CWmin
                        self.LRC = 0
                        self.logger.debug(str(self.nodeid) + ' LRC > ' + str(dot11LongRetryLimit))
                        return False
                else:
                    self.SRC += 1
                    if (self.SRC >= dot11ShortRetryLimit):
                        self.discard()
                        self.CW = CWmin
                        self.SRC = 0
                        self.logger.debug(str(self.nodeid) + ' SRC > ' + str(dot11ShortRetryLimit))
                        return False
                self.snd_frame(self.datatosend)
        else:
            ##self.snd_frame(self.macfsm.memory)
            self.snd_frame(self.datatosend)
        return True

    def snd_frame(self, event):
        self.logger.info(str(self.nodeid) + ' Send Frame')
        txok = False;
        while (txok == False):
            self.logger.debug(str(self.nodeid) + ' Loop LRC: ' + str(self.LRC) + ', SRC: ' + str(self.SRC))
            #if (self.SRC == 0 and self.LRC == 0):        # 1er intento
            #    self.backoff()
            if (not (event.ev_dc['frame_length'] > aRTSThreshold and self.LRC == 0) and not (event.ev_dc['frame_length'] <= aRTSThreshold and self.SRC == 0)):
#                # self.backoff()
#            else:
                self.CW = min(self.CW*2+1, CWmax)
                self.logger.debug(str(self.nodeid) + ' Send Frame new CW ' + str(self.CW))
                self.backoff()
            if (self.freeChannel()):
                self.sendtoL1(event)
                self.logger.debug(str(self.nodeid) + ' Send Frame (done)')
                txok = True
                break;
            self.logger.debug(str(self.nodeid) + ' Send Frame: keep waiting')
        self.logger.debug(str(self.nodeid) + ' Send Frame (done)')
        return True
        
    def sndRTS(self, fsm):
        self.logger.info(str(self.nodeid) + ' Send RTS')
        rcv_event = self.macfsm.memory
        if (rcv_event.ev_subtype == 'CTSTout'):
            if (rcv_event.nickname == 'TimerCTSTout'):
                self.logger.info(str(self.nodeid) + ' Send RTS timer exausted')
                self.set_timer(0, interrupt=True)
                return
        event = events.mkevent("CtrlRTS")
        event.ev_dc['src_addr'] = self.net_conf.station_id
        event.ev_dc['dst_addr'] = rcv_event.ev_dc['dst_addr']
        event.ev_dc['duration'] = 0;
        self.snd_frame(event)
        return True

    def sndCTS(self, fsm):
        self.logger.info(str(self.nodeid) + ' Send CTS')
        event = events.mkevent("CtrlCTS")
        event.ev_dc['src_addr']=self.net_conf.station_id
        rcv_event = self.macfsm.memory
        event.ev_dc['dst_addr']= rcv_event.ev_dc['src_addr']
        self.snd_frame(event)
        return True

    def rcvRTS(self, fsm):
        self.logger.info(str(self.nodeid) + ' Receive RTS')
        self.updNAV(fsm)
        event = self.macfsm.memory
        if (event.ev_dc['dst_addr'] == self.net_conf.station_id):
            self.logger.debug(str(self.nodeid) + ' Receive RTS (for me)')
            self.sndCTS(fsm)
        else:
            self.logger.debug(str(self.nodeid) + ' Receive RTS (not for me, ignoring)')
            self.macfsm.next_state = self.macfsm.current_state
        return True

    def updNAV(self, fsm):
        self.logger.info(str(self.nodeid) + ' Update NAV')
        event = self.macfsm.memory
        if (fsm.input_symbol == "RTS"):
            #waitT = 2*aSIFSTime + CTS_Time + 2*aSlotTime # tutorial
            waitT = 2*aSIFSTime + CTS_Time + aPHY_RX_START_Delay + 2*aSlotTime # norma
            #self.logger.debug(str(self.nodeid) + ' Sleep for ' + str(waitT))
            #time.sleep(waitT)
            self.NAV = waitT
        else:
            testNAV = self.currentTime() + int(event.ev_dc['duration'])
            if (testNAV > self.NAV):
                self.NAV = testNAV
        return True

    def sndACK(self, fsm):
        self.logger.info(str(self.nodeid) + ' Send ACK')
        event = events.mkevent("CtrlACK")
        event.ev_dc['src_addr']=self.net_conf.station_id
        rcv_event = self.macfsm.memory
        event.ev_dc['dst_addr']= rcv_event.ev_dc['src_addr']
        self.snd_frame(event)
        return True

    def rcvACK(self, fsm):
        self.logger.info(str(self.nodeid) + ' Receive ACK')
        event = self.macfsm.memory
        if (event.ev_dc['dst_addr'] == self.net_conf.station_id):
            self.logger.debug(str(self.nodeid) + ' Receive ACK (for me)')
            self.CW = CWmin
            if (event.ev_dc['frame_length'] > aRTSThreshold):
                self.LRC = 0
            else:
                self.SRC = 0
            self.set_timer(1, interrupt=True)
            ## TODO fragmentation 
        else:
            self.logger.debug(str(self.nodeid) + ' Receive ACK (not for me, ignoring)')
            self.macfsm.next_state = self.macfsm.current_state
        return True

    def sendtoL1(self, event):
        self.logger.info(str(self.nodeid) + ' Transmit')
        self.write_out(0, event)
        return True
                
    def backoff(self):
        self.logger.info(str(self.nodeid) + ' Backoff BC: ' + str(self.BC) + ' CW: ' + str(self.CW))
        if (self.BC == 0):
            self.BC = random.randint(0, self.CW)
            self.logger.debug(str(self.nodeid) + ' Backoff new BC: ' + str(self.BC))
        while (self.BC != 0):
            time.sleep(aSlotTime)
            if (max(self.NAV, self.PAV) < (self.currentTime() - aSlotTime)):
                while (not self.freeChannel()):
                    self.waitfree()
                self.BC -= 1
                self.logger.debug(str(self.nodeid) + ' Backoff new BC decrement: ' + str(self.BC))
            else:
                while (not self.freeChannel()):
                    self.waitfree()
                self.logger.debug(str(self.nodeid) + ' Backoff sleep aDIFSTime')
                time.sleep(aDIFSTime)
        return True

    def rcvL1(self, fsm):
        self.logger.info(str(self.nodeid) + ' Receive from L1')
        self.updNAV(fsm)
        event = self.macfsm.memory
        if (event.ev_dc['dst_addr'] == self.net_conf.station_id):
            self.logger.debug(str(self.nodeid) + ' Receive L1 data (for me)')
            self.write_out(1, event)
            time.sleep(aSIFSTime)
            self.sndACK(fsm)
        else:
            self.logger.debug(str(self.nodeid) + ' Receive L1 data (not for me, ignoring)')
            self.macfsm.next_state = self.macfsm.current_state
        return True

    def currentTime(self):
        self.logger.debug(str(self.nodeid) + ' Get current Time')
        return time.time()

    def freeChannel(self):
        self.logger.debug(str(self.nodeid) + ' freeChannel?')
        test = random.randint(0,100);
        if (test > Loses):
            self.logger.debug(str(self.nodeid) + ' freeChannel: FREE')
            return True
        else:
            self.logger.debug(str(self.nodeid) + ' freeChannel: BUSY')
            return False

    def waitfree(self):
        self.logger.debug(str(self.nodeid) + ' waitfree')
        while (not self.freeChannel()):
            time.sleep(1)
        self.logger.debug(str(self.nodeid) + ' waitfree, now free')
        return True

    def discard(self):
        self.logger.debug(str(self.nodeid) + ' discard')
        self.datatosend = 0
        self.macfsm.next_state = 'IDLE'
        return True


def test2():
    '''Test InPort, Block classses.
    blk1 = Timer()
    print blk1
    connector1 = inport.AQueueConnector()
    connector2 = inport.AQueueConnector()
    #blk1.start()
    #time.sleep(2)
    blk1.set_connection_in(connector1,0)
    blk1.set_connection_out(connector1,0)
    blk1.start()
    time.sleep(3)
    event = events.mkevent("TimerConfig")
    event.ev_dc['interval'] = 1
    event.ev_dc['retry'] = 5
    event.ev_dc['nickname1'] = "TimerTOR1"
    connector1.put(event)
        
    time.sleep(10)
    blk1.stop()
    blk1.join()
    #blk1.stop()
    '''

if __name__ == '__main__':
    try:
        test2()
    except KeyboardInterrupt:
        pass




