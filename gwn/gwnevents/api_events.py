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


'''Functions to create events of different types.

To create an event object use function C{mkevent()}. This function creates events of different types, according to the event modules imported by this module.
'''

import sys
import types

import evtimer
import utils.framers.ieee80211.evframes80211 as evframes80211
import evrequest
#sys.path = sys.path + ['..']



def mkevent(nickname, **kwargs):
    '''Returns an event of the given event nickname.

    @param nickname: a valid event nickname, i.e. one that is a key in dictionary of valid nicknames.
    @param kwargs: a dictionary of variables depending on the type of event. Field C{ev_dc} is a dictionary of fields and values for the corresponding event type; field C{frmpkt} is a binary packed frame.
    @return: an Event object.
    '''

    from evtimer import dc_nicknames as ev_dc_nicknames
    import utils.framers.ieee80211.evframes80211
    import evrequest

    frmpkt, ev_dc = '', {}
    if kwargs.has_key('ev_dc'):
        ev_dc = kwargs['ev_dc']
    if kwargs.has_key('frmpkt'):
        frmpkt = kwargs['frmpkt']
        ev_dc['frame_length'] = len(frmpkt)
    else:
        ev_dc['frame_length'] = 0
        frmpkt = ''
    if kwargs.has_key('payload'):
        payload = kwargs['payload']
    else:
        payload = ''
    if evtimer.dc_nicknames.has_key(nickname):
        ptype, psubtype, eventclass = evtimer.dc_nicknames[nickname]
        return eventclass(nickname, ptype, psubtype, ev_dc)    
    elif evframes80211.dc_nicknames.has_key(nickname):
        ev_type, ev_subtype, eventclass = evframes80211.dc_nicknames[nickname]
        ev = eventclass(nickname, ev_type, ev_subtype, frmpkt, ev_dc)
        ev.payload = payload
        return ev
    elif evrequest.dc_nicknames.has_key(nickname):
        ptype, psubtype, eventclass = evrequest.dc_nicknames[nickname]
        return eventclass(nickname, ptype, psubtype, ev_dc)    
    else:
        raise EventNameException(nickname + ' is not a valid nickname.')





if __name__ == '__main__':
    import doctest
    doctest.testmod()


