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

'''Transmit to and receive from layer 1.
'''

from gnuradio import gr


# From gr-digital
#from gnuradio import digital

# from current dir

from transmit_path import transmit_path as tp36
from transmit_path3_7 import transmit_path as tp37

from uhd_interface import uhd_transmitter

from receive_path import receive_path as rp36
from receive_path3_7 import receive_path as rp37

from uhd_interface import uhd_receiver

import sys, threading, math

#import os 
#print os.getpid()
#raw_input('Attach and press enter')

class my_top_block_rx(gr.top_block):
    '''A top block for reception.
    '''
    def __init__(self, demodulator, options, q_rx):
        '''Constructor.
        
        @param demodulator:
        @param options:
        @param q_rx:
        '''
        gr.top_block.__init__(self)

        if(options.rx_freq is not None):
            # Work-around to get the modulation's bits_per_symbol
            args = demodulator.extract_kwargs_from_options(options)
            symbol_rate = options.bitrate / \
                demodulator(**args).bits_per_symbol()

            self.source = uhd_receiver(options.args, symbol_rate,
                options.samples_per_symbol,
                options.rx_freq, options.rx_gain,
                options.spec, options.antenna,
                options.verbose)
            options.samples_per_symbol = self.source._sps

        elif(options.from_file is not None):
            sys.stderr.write(("Reading samples from '%s'.\n\n" % \
                (options.from_file)))
            self.source = gr.file_source(gr.sizeof_gr_complex, \
                options.from_file)
        else:
            sys.stderr.write( \
                "No source defined, pulling samples from null source.\n\n")
            self.source = gr.null_source(gr.sizeof_gr_complex)
        self.q_rx =q_rx
        # Set up receive path
        # do this after for any adjustments to the options that may
        # occur in the sinks (specifically the UHD sink)
        if options.version == '6':
            self.rxpath = rp36(demodulator, self.rx_callback, options) 
        if options.version == '7':
            self.rxpath = rp37(demodulator, self.rx_callback, options) 
            
        self.connect(self.source, self.rxpath)
    
    def rx_callback(self,ok, payload):
        '''A callback function for reception.
        '''
        print " LLEGO PAYLOAD-------------------------------------------------"
        print payload
        print "--------------------------------------------------"
        self.q_rx.put(payload)
  
    def set_freq(self,value):
        self.source.set_freq(value)
        
    def sense_carrier(self):
        print "Energy : ",
        print 10*math.log10(self.rxpath.carrier_sensed())


class my_top_block_tx(gr.top_block):
    '''A top block for transmission.
    '''
    
    def __init__(self, modulator, options, q_tx):
        '''Constructor.
        
        @param modulator:
        @param options:
        @param q_tx:
        '''
        gr.top_block.__init__(self)

        if(options.tx_freq is not None):
            # Work-around to get the modulation's bits_per_symbol
            args = modulator.extract_kwargs_from_options(options)
            symbol_rate = options.bitrate / modulator(**args).bits_per_symbol()

            self.sink = uhd_transmitter(options.args, symbol_rate,
                options.samples_per_symbol,
                options.tx_freq, options.tx_gain,
                options.spec, options.antenna,
                options.verbose)
            options.samples_per_symbol = self.sink._sps
            
        elif(options.to_file is not None):
            sys.stderr.write(("Saving samples to '%s'.\n\n" % \
                (options.to_file)))
            self.sink = gr.file_sink(gr.sizeof_gr_complex, options.to_file)
        else:
            sys.stderr.write( \
                "No sink defined, dumping samples to null sink.\n\n")
            self.sink = gr.null_sink(gr.sizeof_gr_complex)
        self.tx_l1 = TxL1(self, q_tx,options)
        self.tx_l1.start()
        # do this after for any adjustments to the options that may
        # occur in the sinks (specifically the UHD sink)
        if options.version == '6':        
            self.txpath = tp36(modulator, options)
        if options.version == '7':
            self.txpath = tp37(modulator, options)
        self.connect(self.txpath, self.sink)

    def set_freq(self, value):
        self.sink.set_freq(value)
  
        
        
class TxL1(threading.Thread):
    '''A control thread for transmission / reception into layer 1.
    '''
    
    def __init__(self, tb, q_tx, options):
        '''Constructor.
        
        @param tb:
        @param q_tx:
        @param options:
        '''
        threading.Thread.__init__(self)
        self.tb = tb
        self.q_tx =q_tx
        self.finished = False
        self.options =options

    def run(self):
        while not self.finished:
            payload = self.q_tx.get()
            print " -------------------------------------------------"
            print payload
            print "--------------------------------------------------"
            self.tb.txpath.send_pkt(payload)    
                
        self.tb.txpath.send_pkt("", True)
        print("TxL1 ends")    
                
    def stop(self):
        self.finished=True
        self._Thread__stop()
  
  