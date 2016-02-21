#############################################
# MISP API miscellaneous functions.
# 
# Author: Emmanuel Bouillon
# Email:  emmanuel.bouillon.sec@gmail.com
# Date: 24/11/2015
#############################################

# MISP BASE URL
BASE_URL = '<MISP_BASE_URL>'
# API KEY
API_KEY = '<YOUR_API_KEY>'
# MISP_VERIFYCERT
MISP_VERIFYCERT = True
# pyMISP DEBUG
MISP_DEBUG = False

from pymisp import PyMISP
from MaltegoTransform import *

def init():
    return PyMISP(BASE_URL, API_KEY, MISP_VERIFYCERT, 'json', MISP_DEBUG)

def retrieveEvents(mt, enFilter, enValue):
    misp = init()
    result = misp.search(values = enValue, type_attribute = enFilter)
    for e in result['response']:
        eid = e['Event']['id']
        einfo = e['Event']['info']
        eorgc = e['Event']['Orgc']['name']
        me = MaltegoEntity('maltego.MISPEvent',eid);
        me.addAdditionalFields('EventLink', 'EventLink', False, BASE_URL + '/events/view/' + eid )
        me.addAdditionalFields('Org', 'Org', False, eorgc)
        me.addAdditionalFields('notes#', 'notes', False, eorgc + ": " + einfo)
        mt.addEntityToMessage(me);
    return

