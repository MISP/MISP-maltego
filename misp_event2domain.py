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

type2attribute = {'domain':('domain','hostname'), 'hostname':('hostname'), 'hash':('md5','sha1','sha256') , 'ip':('ip-src','ip-dst'), 'email':('email-src','email-dst'), 'email-subject': ('email-subject')}
argType2enType = {'domain':'maltego.Domain', 'hostname':'maltego.Domain', 'hash':'maltego.Hash', 'ip':'maltego.IPv4Address', 'email':'maltego.EmailAddress', 'email-subject': 'maltego.Phrase'}
filename_pipe_hash_type = ('filename|md5', 'filename|sha1', 'filename|sha256', 'malware-sample')

if __name__ == '__main__':
        event_id = sys.argv[1]
        argType = sys.argv[0].split('.')[0].split('2')[1] # misp_event2argType.py
        misp = init()
        mt = MaltegoTransform()
        try:
            event_json = misp.get_event(event_id)
            for attribute in event_json['Event']["Attribute"]:
                value = attribute["value"]
                aType = attribute["type"]
                comment = attribute['comment']
                if aType in type2attribute[argType]:
                    if aType in filename_pipe_hash_type:
                        h = value.split('|')[1].strip()
                        me = MaltegoEntity(argType2enType[argType], h)
                        mt.addEntityToMessage(me);   
                    else:
                        me = MaltegoEntity(argType2enType[argType], value)
                    if 0 < len(comment) < 32:
                        me.addAdditionalFields('notes#', 'notes', False, comment)
                    mt.addEntityToMessage(me);
        except Exception as e:
            mt.addUIMessage("[ERROR]  " + str(e))
        mt.returnOutput()
