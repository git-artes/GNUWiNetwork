#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mac_api : an API to use the library.

'''An API to access the frame classes and functions.

@var dc_mactypobjs: a dictionary (type, subtype, object) of frame names and an object of the corresponding type.
'''

import mac_ctrl, mac_data, mac_mgmt
from mac_frcl import FCframe



dc_frametypes = { \
    ('Ctrl','RTS'):'RTS', \
    ('Ctrl','CTS'):'CTS', \
    ('Ctrl','ACK'):'ACK', \
    ('Data','DATA'):'DATA', \
    ('Mgmt','Beacon'):'Becon' \
    }

def mkdcframetypes():
    '''Makes a dictionary of objects, one for each (type, subtype).
    '''
    dc_frmobjs = {}
    dc_frmobjs['FC']   = FCframe()
    dc_frmobjs['RTS']  = mac_ctrl.RTSframe()
    dc_frmobjs['CTS']  = mac_ctrl.CTSframe()
    dc_frmobjs['ACK']  = mac_ctrl.ACKframe()
    dc_frmobjs['DATA'] = mac_data.DATAframe()
    dc_frmobjs['Beacon'] = mac_mgmt.MgmtFrame()
    return dc_frmobjs

dc_frmobjs = mkdcframetypes()

def getfrmobj(ptype, psubtype):
    '''Returns a pointer to a MAC frame object of the given type, subtype.
    '''
    if dc_frametypes.has_key( (ptype, psubtype) ):
        objtype = dc_frametypes[ (ptype, psubtype) ]
        return dc_frmobjs[objtype]
    else:
        return None


def mkdcfrmobjs():
    '''Makes a dictionary {frame type: object} for supported frame types.
    
    This function creates one object of each type of frame to avoid repeated creation of objects, a costly operation. Objects are kept in a dictionary by type of frame.
    @return: a dictionary of frame objects by type of frame.
    '''
    dc_frmobjs = {}
    dc_frmobjs['FC']   = FCframe()
    dc_frmobjs['RTS']  = mac_ctrl.RTSframe()
    dc_frmobjs['CTS']  = mac_ctrl.CTSframe()
    dc_frmobjs['ACK']  = mac_ctrl.ACKframe()
    dc_frmobjs['DATA'] = mac_data.DATAframe()
    dc_frmobjs['Beacon'] = mac_mgmt.MgmtFrame()
    return dc_frmobjs

dc_frmobjs = mkdcfrmobjs()

def mkfrpkt(frmtype, dc_frmobjs=dc_frmobjs, fc_dc_fldvals={}, fr_dc_fldvals={}):
    '''Make frame packet of frame of a given type, optionally updating field values.
    
    This function packs a frame of indicated frame type, optionally updating values in frame control fields or frame fields. Returns a packed frame.
    B{WARNING}: values not updated are kept in previous value, as set in previous use of the object.
    @param frmtype: the type of frame.
    @param dc_frmobjs: dictionary of frame objects by type of frame.
    @param fc_dc_fldvals: optional field values dictionary to update frame control field.
    @param fr_dc_fldvals: optional field values dictionary to update MAC frame fields.
    @return: a frame object of given type.
    '''
    if frmtype not in FCframe.dc_frmtype.keys():
        print 'mkfrpkt: wrong frame type', frmtype
        return None
    else:
        dc_frmobjs['FC'].setfctype(frmtype)                # set FC field for frame type
        dc_frmobjs['FC'].updtfldvals(fc_dc_fldvals)        # update FC field values
        dc_frmobjs[frmtype].updtfldvals(fr_dc_fldvals)     # update frame field values

        return dc_frmobjs['FC'].mkpkt() + dc_frmobjs[frmtype].mkpkt()[2:]


def mkdics(frmpkt, dc_frmobjs=dc_frmobjs):
    '''Makes dictionaries {field: value} for Frame Control and MAC frames.
    
    This function unpacks a packed frame, decodes the frame control in first two bytes, and uses the corresponding frame object to buil dictionaries of {field, value}. Returns frame type, dictionary of frame control field values, dictionary of frame field values.
    @return: a tuple (frmtype, dc_fc_fldvals, dc_fr_fldvals) with frame type and two dictionaries.
    '''
    fc_dic = dc_frmobjs['FC'].mkdic(frmpkt[:2])
    for typ in FCframe.dc_frmtype.keys():
        if FCframe.dc_frmtype[typ]['ProtVer'] == fc_dic['ProtVer'] and \
            FCframe.dc_frmtype[typ]['Type'] == fc_dic['Type'] and \
            FCframe.dc_frmtype[typ]['SubType'] == fc_dic['SubType']:
            frmtype = typ
            break
    fr_dic = dc_frmobjs[frmtype].mkdic(frmpkt)
    return frmtype, fc_dic, fr_dic



