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
A TUN/TAP interface connector and block.

Use the Universal TUN/TAP device driver to move packets to/from kernel.
See /usr/src/linux/Documentation/networking/tuntap.txt
'''

import fcntl
import os
import struct
import subprocess

import threading

import Queue
import time
import sys

try:
    import gwnblocks.gwninport as gwninport
    import gwnblocks.gwnblock as gwnblock
    import gwnevents.api_events as events
except ImportError:
    print 'tuntap.py, import Error:'
    print '  adjust PYTHONPATH for sudo:'
    print '    sudo env PYTHONPATH=<your_gwn_path>/gwn/ python tuntap.py'
    sys.exit()


class ATunTapConnector(gwninport.Connector):
    '''A Connector with a TUN/TAP interface.
    '''


    def __init__(self, device='/dev/net/tun'):

        # Linux specific...
        # TUNSETIFF ifr flags from <linux/tun_if.h>
        # constants used to ioctl the device file
        IFF_TUN		= 0x0001   # tunnel IP packets
        IFF_TAP		= 0x0002   # tunnel ethernet frames
        IFF_NO_PI	= 0x1000   # don't pass extra packet info
        IFF_ONE_QUEUE	= 0x2000   # beats me ;)
        TUNSETIFF = 0x400454ca

        mode = IFF_TAP | IFF_NO_PI
        self.tun_fd = os.open(device, os.O_RDWR)
        ifs = fcntl.ioctl(self.tun_fd, TUNSETIFF, struct.pack("16sH", "gr%d", mode))
        self.tun_ifname = ifs[:16].strip("\x00")

        print "Virtual ethernet interface: %s, use ifconfig to set IP address:" % \
            (self.tun_ifname,)
        print "  $ sudo ifconfig %s 192.168.200.1" % (self.tun_ifname,)

    def get(self):
        '''Read from the operating system, return payload.

        @return: payload, a data unit received from the operating system, or None.
        '''
        payload = payload = os.read(self.tun_fd, 10*1024)
        if payload:
            return payload
        else:
            return None


    def put(self, payload):
        '''Write to the operating system.

        @param payload: a data unit to transfer to the operating system.
        '''
        try:
            os.write(self.tun_fd, payload)
        except:
            print " OS payload error ", repr(payload)



class TunTapInterface(gwnblock.GWNBlock):
    '''A TUN/TAP interface block.
    '''

    def __init__(self, device='/dev/net/tun', my_addr='0.0.0.0', dst_addr='0.0.0.0'):
        '''Constructor.

        A block with an input port and an output por on which events are received and sent. Read and write operations on the TUN/TAP interface happen through TUN/TAP connector instances. A TUN/TAP connector instance is assigned through an InPort for input; the same TUN/TAP connector instance is assigned as an output port, since communications is with the operating system in this node, and TUN/TAP connector instances support both get() and put() operations.
        @param device: the TUN/TAP device, default value /dev/net/tun.
        @param my_addr: address of this node.
        @param dst_addr: address of destination node.
        '''
        super(TunTapInterface, self).__init__(1,'TunTapInterface', 2, 2)

        conn = ATunTapConnector(device)
        self.set_connection_in(conn, 1)
        self.set_connection_out(conn, 1)

        self.device = device
        self.my_addr = my_addr
        self.dst_addr = dst_addr


    def process_data(self, port_type, port_nr, ev):
        '''Block specific processing.

        @param port_type: the type of port, a string.
        @param port_nr: the port number on which the event was received.
        @param ev: an Event object.
        '''
        print 'Processing, block %s, port %s %d, event %s... ' % \
            (self.blkname, port_type, port_nr, ev),

        if port_type is 'inport' and port_nr is 1:     # ev is payload from op sys
            event = events.mkevent("DataData")
            event.ev_dc['src_addr'] = self.my_addr
            event.ev_dc['dst_addr'] = self.dst_addr
            event.payload = ev
            self.write_out(0, event)

            # to implement through gnlogger
            print '===> Received payload, send Event ===>'
            print event
            print repr(event.payload)
            print

        elif port_type is 'inport' and port_nr is 0:   # ev is event from other block
            payload = ev.payload
            self.write_out(1, payload)

            # to implement through gnlogger
            print '===> Received Event, send payload ===>'
            print ev
            print repr(payload)
            print

        else:
            return


### testing


def test1():
    '''Tests ATunTapConnector class.
    '''
    conn = ATunTapConnector()
    for i in range(0,3):
        payload = conn.get(),
        print "Got", repr(payload)
        conn.put(payload)
        print "Sent", repr(payload)
    print


def test2():
    blk2 = TunTapInterface('/dev/net/tun', '192.168.200.1', '192.168.200.2')

    conn_ev1 = gwninport.AQueueConnector(10)
    conn_ev2 =  gwninport.AQueueConnector(10)
    blk2.set_connection_in(conn_ev1, 0)
    blk2.set_connection_out(conn_ev2, 0)

    print 'port in 0:', blk2.ports_in[0].conn.__class__
    print 'port in 1:', blk2.ports_in[1].conn.__class__
    print 'port out 0:', blk2.ports_out[0].__class__
    print 'port out 1:', blk2.ports_out[1].__class__

    #sys.exit()

    print 'Set up IP address 192.168.7.1 in TUN/TAP connector,'
    print '  captures all incoming packets, ensures process finishes.'
    subprocess.check_call('ifconfig gr0 192.168.7.1', shell=True)
    time.sleep(2)   # to read message :-)
    #subprocess.check_call('ifconfig tun0 192.168.7.1 %s up' % (self.tun_ifname,), \
    #    shell=True)
    #subprocess.check_call('ifconfig %s 192.168.7.1' % (self.tun_ifname,), \
    #        shell=True)

    blk2.start()    
    time.sleep(3)

    for i in range(0,5):
        print '=== BEGIN Event %d ===' % (i,)
        event = events.mkevent('DataData', ev_dc={'src_addr':'sss', \
            'dst_addr':'dddd'} )
        blk2.ports_in[0].conn.put(event)
        time.sleep(2)
        print '=== END Event %d ===' % (i,)

    time.sleep(5)

    blk2.stop()
    time.sleep(2)
    #blk2.ports_in[0].conn.put('0000')  # to make is stop
    #subprocess.check_call('ping -c1 192.168.7.1')
    #print '1', threading.enumerate()
    blk2.join()

    #print '2', threading.enumerate()





if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '1':
            test = test1
        elif sys.argv[1] == '2':
            test = test2
    else:
        test = test2
        #print 'tuntapport: please do'
        #print '   python tuntapport.py <number of test to run: 2, 3 or 4> '

    try:
        test()
    except KeyboardInterrupt:
        pass
