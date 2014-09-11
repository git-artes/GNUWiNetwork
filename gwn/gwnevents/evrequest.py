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


'''A library for block configuration events.

@var dc_nicknames: a dictionary of nicknames, types, subtypes, and classnames, C{ {nickname: (type, subtype, classname)} }; C{classname} is the class used to build the object. This dictionary allows to build a time event object by just saying its nickname. Module function C{mkevent()} uses this module variable.
'''

from gwnevent import Event, EventNameException



class EventRequest(Event):
    '''An event associated with the configuration of blocks.
    
    @ivar nickname: a descriptive name for this event.
    @ivar ev_type: timer event type.
    @ivar ev_subtype: timer event subtype.
    @ivar ev_dc: a dictionary of complementary data, e.g. {'add_info': 'additional information'}.
    '''
    
    def __init__(self, nickname, ev_type, ev_subtype, ev_dc={}):
        '''Constructor.
        '''
        self.nickname = nickname
        self.ev_type = ev_type
        self.ev_subtype = ev_subtype
        self.ev_dc = {}
        self.ev_dc.update(ev_dc)
        return




dc_nicknames = { \
	'TimerConfig'        : ('Request',  'SetTimerConfig',     EventRequest     ), \
	'EventConsumerStatus'  : ('Request',  'EventConsumerStatus', EventRequest     ) \
    }



if __name__ == '__main__':
    import doctest
    doctest.testmod()



