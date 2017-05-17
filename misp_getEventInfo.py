#############################################
# MISP API Domain to Event
# 
# Author: Emmanuel Bouillon
# Email:  emmanuel.bouillon.sec@gmail.com
# Date: 24/11/2015
#############################################
import sys
from misp_util import *
from pymisp import PyMISP
import json

if __name__ == '__main__':
        m = init()
        mt = MaltegoTransform()
        event_id = sys.argv[1]
        try:
            event_json = m.get_event(event_id)
            eid = event_json['Event']['id']
            einfo = event_json['Event']['info']
            eorgc = event_json['Event']['Orgc']['name']
            me = MaltegoEntity('maltego.MISPEvent',eid);
            me.addAdditionalFields('EventLink', 'EventLink', False, BASE_URL + '/events/view/' + eid )
            me.addAdditionalFields('Org', 'Org', False, eorgc)
            me.addAdditionalFields('notes#', 'notes', False, eorgc + ": " + einfo)
            mt.addEntityToMessage(me);
        except Exception as e:
            mt.addUIMessage("[ERROR]  " + str(e))
        mt.returnOutput()
