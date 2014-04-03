#!/usr/bin/env python
#
# Copyright 2010,2011 Free Software Foundation, Inc.
# 
# This file is part of GNU Radio
# 
# GNU Radio is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# GNU Radio is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with GNU Radio; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 
import sys
sys.path +=['..']
from gnuradio import gr
from gnuradio.eng_option import eng_option
from optparse import OptionParser

# From gr-digital
from gnuradio import digital

# from current dir
from transmit_path import transmit_path as tp36
from transmit_path import transmit_path as tp37

from uhd_interface import uhd_transmitter

from receive_path import receive_path as rp36
from receive_path3_7 import receive_path as rp37
from uhd_interface import uhd_receiver
import TxRxLayer1
import time, struct, sys, threading,Queue
import libmanagement.NetworkConfiguration as NetworkConfiguration
import libmanagement.DiscoveryPeeringController as DiscoveryPeeringController
import libmanagement.Beacon as Beacon
import libadaptlay80211.schedEvToFr as schedEvToFr
import libadaptlay80211.schedFrToEv as schedFrToEv
import libadaptlay80211.schedLayer3 as schedLayer3

        

# /////////////////////////////////////////////////////////////////////////////
#                                   main
# /////////////////////////////////////////////////////////////////////////////
class StartSchedL1_L2:

    def __init__(self, q_rx,q_tx,mac_addr):
        self.q_rx =q_rx
        self.q_tx = q_tx
        self.isrunning = False
        self.ctrl_q, self.mgmt_q, self.data_q = Queue.Queue(10), Queue.Queue(10), Queue.Queue(10)
        self.out_queues = { \
            'Ctrl': (self.ctrl_q), \
            'Mgmt': (self.mgmt_q), \
            'Data': (self.data_q)  \
            }
        frame_tx_q = self.q_tx
        self.tx_ev_q = Queue.Queue(10)
        self.out_queues_tx = { \
            'frames':    (frame_tx_q) \
        }


        return

    def start(self):
        self.isrunning = True
        " Configuration of the Scheduler of Node 1 that recieves frames and generates management events."
        self.sch1 = schedFrToEv.SchedFrToEv(self.q_rx, self.out_queues)
        self.sch1.start()
        
        "Configuration of the scheduler of Node 1 that recieves events and generates frame events."
        self.tx1 = schedEvToFr.SchedEvToFr(self.tx_ev_q, self.out_queues_tx)
        self.tx1.start()



    def stop(self):
         if self.isrunning == True:
             self.sch1.stop()     
             self.tx1.stop()
             self.isrunning = False


class StartL2Mgmt:

    def __init__(self, mgmt_ev_q,tx_ev_q,mac_addr,broadcast_addr,network_id):
        self.mgmt_ev_q =mgmt_ev_q
        self.tx_ev_q = tx_ev_q
        self.mac_addr = mac_addr
        self.broadcast_addr = broadcast_addr
        " Network configuration: the MAC Addr, the name of the network and the broadcast Addr"    
        self.net_conf1 = NetworkConfiguration.NetworkConfiguration(self.mac_addr,network,"256",broadcast_addr)
        self.net_conf1.retry_timeout = 5  
        self.isrunning = False
        return

    def start(self):
        self.isrunning = True
        " Starts the Controller of The FSM for Peering Discovering"
        self.dpcontrol1 =  DiscoveryPeeringController.DiscoveryPeeringController(self.net_conf1,None,self.mgmt_ev_q,self.tx_ev_q1)
        self.dpcontrol1.start()
        "Starts the beacon generator of this node"
        self.myBeacon1 = Beacon.Beacon(self.net_conf1 ,self.tx_ev_q1)
        self.myBeacon1.start()          

    def stop(self):
         if self.isrunning == True:
             self.dpcontrol1.stop()
             self.myBeacon1.stop()
             self.isrunning = False

class StartL1():

    def __init__(self, q_rx,q_tx,options,modulator,demodulator):
       
        self.q_rx =q_rx
        self.q_tx = q_tx
        self.options = options
        self.demodulator =demodulator
        self.modulator = modulator
        return

    def start(self):

        self.tb_rx = TxRxLayer1.my_top_block_rx(self.demodulator, self.options,self.q_rx)
        self.tb_rx.start()        # start flow graph
        self.tb = TxRxLayer1.my_top_block_tx(self.modulator, self.options,self.q_tx)
        self.tb.start() 

    def set_rx_freq(self,value):            
        self.tb_rx.set_freq(value)

    def set_tx_freq(self,value):            
        self.tb.set_freq(value)

    def sense_carrier(self):
        self.tb_rx.sense_carrier()


    def stop(self):
        self.tb.tx_l1.stop()
        self.tb.stop()
        self.tb.wait()   
        print("tx top block stopped")
        self.tb_rx.stop()                    # wait for it to finis
        self.tb_rx.wait()         # wait for it to finish
        print("rx top block stopped")



def main():
    mods = digital.modulation_utils.type_1_mods()
    demods = digital.modulation_utils.type_1_demods()
    parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
    expert_grp = parser.add_option_group("Expert")

    parser.add_option("-m", "--modulation", type="choice", choices=mods.keys(),
                      default='bpsk',
                      help="Select modulation from: %s [default=%%default]"
                            % (', '.join(mods.keys()),))

    parser.add_option("-s", "--size", type="eng_float", default=100,
                      help="set packet size [default=%default]")
    parser.add_option("-M", "--megabytes", type="eng_float", default=1.0,
                      help="set megabytes to transmit [default=%default]")
    parser.add_option("","--discontinuous", action="store_true", default=False,
                      help="enable discontinous transmission (bursts of 5 packets)")
    parser.add_option("","--from-file", default=None,
                      help="use intput file for packet contents")
    parser.add_option("","--to-file", default=None,
                      help="Output file for modulated samples")
    parser.add_option("", "--mac", default=None , help = "MAC addres")
    parser.add_option("", "--version", default='6' , help = "gnuradio version, default 6 (3.6)")
    parser.add_option("", "--mac_dst", default=None , help = "Destination MAC addres")
     
    tp36.add_options(parser, expert_grp)
    tp37.add_options(parser, expert_grp)

    uhd_transmitter.add_options(parser)
  
    rp36.add_options(parser, expert_grp)
    rp37.add_options(parser, expert_grp)
    uhd_receiver.add_options(parser)

    for mod in demods.values():
        mod.add_options(expert_grp)
    for mod in mods.values():
        mod.add_options(expert_grp)
    (options, args) = parser.parse_args ()
    if len(args) != 0:
        parser.print_help()
        sys.exit(1)           
    if options.from_file is not None:
        source_file = open(options.from_file, 'r')
    r = gr.enable_realtime_scheduling()
    if r != gr.RT_OK:
        print "Warning: failed to enable realtime scheduling"
    q_tx =Queue.Queue(10)
    q_rx =Queue.Queue(10) 
    l1=StartL1(q_rx,q_tx,options,mods[options.modulation],demods[options.modulation])
    l1.start()
    schL1_L2= StartSchedL1_L2(q_rx,q_tx,options.mac)
    schL1_L2.start()
# POR AHORA NO USO CAPA MAC
#    l2Mgmt=StartL2Mgmt(schL1_L2.mgmt_q1,schL1_L2.tx_ev_q,options.mac,"256","Red IIE")
#    l2Mgmt.start()

    l3= schedLayer3.Layer3(schL1_L2.tx_ev_q,schL1_L2.data_q,'/dev/net/tun',options.mac,options.mac_dst)

    c = raw_input('Press #z to end, or #w to test commands :')        
    while c != "#z":
       c = raw_input('Press #z to end, or #w to test commands :')        
           
    print "Program ends"
    l3.stop()
    schL1_L2.stop()
    l1.stop()
    #POR AHORA NO ESTOY USANDO CAPA 2
#    l2.stop()
    exit(0)
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
