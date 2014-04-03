#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''Use of events with string frames, version 2.

This module uses a simplified frame format based on strings, aimed at testing; a primary concern is legilibilty, though some packing is done to keep frame length short.

This module defines two functions, mkevent() to make an Event object from a nickname or string frame, and mkframe() to make a string frame from an Event object.

Packet format:

    - nickname, a string.
    - payload length in string format.
    - dictionary of other fields in string format.
    - payload, a string.

Fields are separated by ','. Payload length is required to unpack, since ',' may be included in string format of dictionary or payload.

'''

import events
import if_events
import sys


def mkevent(pnickname=None, pframe=None, pev_dc={}, payload=''):
    '''Creates an event from a nickname or from a frame.
    
    This function accepts either an event nickname or a string frame, but not both. If an event nickname is given, an Event object of that nickname is created; if a string frame is given, an Event object is created from that frame.
    @param pnickname: the event nickname, default None.
    @param pframe: a frame in string format, default None.
    @param pev_dc: a dictionary {field_name: value} for event creation; defaults to an empty dictionary. Disregarded if a frame is given.
    @param payload: the payload, not included in dictionary to preserve binary string format as received.
    @return: an Event object.
    '''
    if not pnickname and not pframe:
        raise events.EventNameException('No event nickname or frame received')
    if pnickname and pframe:
        raise events.EventNameException( \
            'Both event nickname and frame received')
    if pnickname:
        return if_events.mkevent(pnickname, ev_dc=pev_dc)
    if pframe:
        ev_dc = {}
        ### unpack frame
        try:
            nickname, sep, rest1 = pframe.partition(',')
            strlen, sep, rest2 = rest1.partition(',')
            if int(strlen) == 0:
                str_ev_dc = rest2
            else:
                str_ev_dc, payload = rest2[:-int(strlen)], rest2[-int(strlen):]
            ev_dc = eval(str_ev_dc)

            # TODO: this function should adjust frame_length. How?
            #    frame_lenght must be set in ev_dc of Event. Is it used?
        except:
            print "mkevent unpack error : ",repr(pframe)
            return None
        try:
            ev = if_events.mkevent(nickname, frmpkt=pframe, ev_dc=ev_dc)
            ev.payload = payload
            return  ev
        except:
            #raise events.EventNameException( \
            #    'cannot generate event: malformed packet\n' + \
            #    pframe)
            print 'evstrframes: cannot generate event: malformed packet'
            print repr(pframe)
            return None



def mkframe(ev_obj):
    '''Creates a string frame from an Event object.
    
    Receives an Event object, returns a string frame with the event information.
    @param ev_obj: an Event object.
    @return: a frame in string format.
    '''
    if not isinstance(ev_obj, events.Event):
        raise EventNameException('Parameter is not an Event object.')
        return None

    # unnecessary, ev_dc always included in mkevent, even if empty
    #if not ev_obj.ev_dc:
    #    raise if_events.EventNameException('ev_dc not in event object.')

    # TODO: see if all these validations are required, or force fields
    #   to be present by other means, e.g. a default ev_dc
    # WARNING: following lines impose values on these fields!
    #if not ev_obj.ev_dc.has_key('src_addr') or \
    #    not ev_obj.ev_dc.has_key('dst_addr'):
    #    raise if_events.EventNameException( \
    #        'ev_dc does not contain src_addr, dst_addr keys.')
    #if not ev_obj.nickname:
    #    raise if_events.EventNameException( 'even with no nickname.')
    if not ev_obj.ev_dc['src_addr']:
        ev_obj.ev_dc['src_addr'] = ''
    if not ev_obj.ev_dc['dst_addr']:
        ev_obj.ev_dc['dst_addr'] = ''
    if not ev_obj.ev_dc['peerlinkId']:
        ev_obj.ev_dc['peerlinkId'] = 0
    ### end of WARNING
    #
    # frame_length cannot be included in packet, alters frame_length!
    #    other encoding must be used to inclue frame_length in packet
    ### pack frame
    frame = '' + ev_obj.nickname + ',' + str(len(ev_obj.payload)) + ',' + \
        str(ev_obj.ev_dc) + ev_obj.payload
    #print "mkframe   ", frame
    ev_obj.frmpkt = frame
    ev_obj.ev_dc['frame_length'] = len(ev_obj.frmpkt)
    return frame


if __name__ == '__main__':
    import doctest
    testfilename = sys.argv[0][:-2] + 'txt'
    try:
        doctest.testfile(testfilename)
    except:      # no text file present
        pass



