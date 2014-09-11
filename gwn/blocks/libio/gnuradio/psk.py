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

'''PSK modulation transmit / receive block.
'''

import sys
sys.path +=['..']

from gnuradio import digital
import gwnevents.api_events as events
import TxRxLayer1 as TxRxLayer1
import gwnblocks.gwnblock as gwn


class PSK(gwn.GWNBlock):
    '''PSK modulation block.
    '''

    def __init__(self, samples_per_symbol=2, version='6', antenna='TX/RX', \
        rx_freq=850000000.0, rx_gain=15.0, spec='A:0', tx_gain=15.0, \
        modulation='bpsk', args='serial=E0R11Y0B1', bitrate=100000.0, \
        tx_freq=851000000.0, tx_amplitude=0.25):
        '''Constructor.
        
        @param samples_per_symbol: default 2.
        @param version: default 6.
        @param antenna: default TX/RX.
        @param rx_freq: reception frequency, default 850000000.0.
        @param rx_gain: reception gain, default 15.0.
        @param spec: default 'A:0'.
        @param tx_gain: transmission gain, default 15.0.
        @param modulation: default 'bpsk'.
        @param args: default 'serial=E0R11Y0B1'.
        @param bitrate: default 100000.0.
        @param tx_freq: transmission frequency, default 851000000.0.
        @param tx_amplitude: default 0.25.
        '''
        super(PSK,self).__init__(1, 'GNURadioPSK', 2, 2)
        #super(TunTapInterface, self).__init__(1,'TunTapInterface', 2, 2)
        self.mods = digital.modulation_utils.type_1_mods()
        self.demods = digital.modulation_utils.type_1_demods()
        opt = {'verbose':True, 'samples_per_symbol':2, 'chbw_factor':1.0, 'log':False, 'version':'6', 'antenna':'TX/RX', 'rx_freq':850000000.0, 'version':'6', 'rx_gain':15.0, 'spec':'A:0', 'tx_gain':15.0, 'modulation':'bpsk', 'args':'serial=E0R11Y0B1', 'freq':None, 'bitrate':100000.0, 'from_file':None, 'to_file':None, 'tx_freq':851000000.0, 'tx_amplitude':0.25}        
        self.options = dotdict(opt)        
        self.options.samples_per_symbol = samples_per_symbol
        self.options.version = version
        self.options.antenna = antenna
        self.options.rx_freq = rx_freq
        self.options.rx_gain = rx_gain
        self.options.spec = spec
        self.options.tx_gain = tx_gain
        self.options.modulation = modulation
        self.options.args = args
        self.options.bitrate = bitrate
        self.options.tx_freq = tx_freq
        self.options.tx_amplitude = tx_amplitude

        self.rx_conn = gwn.gwninport.AQueueConnector()
        self.tx_conn = gwn.gwninport.AQueueConnector()
        self.rx_queue = self.rx_conn.lsevents
        self.tx_queue = self.tx_conn.lsevents
        self.set_connection_in(self.rx_conn, 1)
        self.set_connection_out(self.tx_conn, 1)

        print 'PSK:', self.mods
        self.demodulator = self.demods[self.options.modulation]
        self.modulator = self.mods[self.options.modulation]
        self.tb_rx = TxRxLayer1.my_top_block_rx(self.demodulator, \
            self.options, self.rx_queue)
        self.tb_tx = TxRxLayer1.my_top_block_tx(self.modulator, \
            self.options, self.tx_queue)
        self.tb_rx.start()        # start flow graph
        self.tb_tx.start()
        return


    def process_data(self, port_type, port_nr, ev):
        '''Process data function for PSK block.
        '''
        print " ------------------------------------"
        print ev
        print port_type,port_nr
        print "-------------------------------------"
        
        if port_type == 'inport' and port_nr == 0:
            frame = ev.frmpkt
            self.write_out(1, frame)    # 1, to GNU radio
        elif port_type == 'inport' and port_nr == 1:
            frame = ev   # ev is a frame received
            if not frame:
                print 'PSK: an empty frame from  L1'
            else:
                event = events.mkevent("DataData")
                event.frmpkt = frame
                self.write_out(0, event)
        return


    def set_rx_freq(self, value):
        '''Set receive frequency.
        '''
        self.tb_rx.set_freq(value)

    def set_tx_freq(self, value):
        '''Set transmit frequency.
        '''
        self.tb.set_freq(value)

    def sense_carrier(self):
        '''Sense carrier function.
        '''
        self.tb_rx.sense_carrier()

    def stop(self):
        '''PSK block stop function.

        This stop function is required to stop GNU Radio threads. Overwrites generic block stop function; first stops locally started threads, waits on them, and finally invokes the generic stop function in PSK super class (generic block).
        '''
        self.tb_tx.stop()
        self.tb_tx.wait()   
        print("tx top block stopped")
        self.tb_rx.stop()         # wait for it to finish
        self.tb_rx.wait()         # wait for it to finish
        print("rx top block stopped")
        super(PSK, self).stop()


class dotdict(dict):
        '''dot.notation access to dictionary attributes.
        '''
        def __getattr__(self, attr):
            return self.get(attr)
        __setattr__= dict.__setitem__
        __delattr__= dict.__delitem__        

        
def main():
    g = PSK()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

