#############################################
# MISP API Domain to Event
# 
# Author: Emmanuel Bouillon
# Email:  emmanuel.bouillon.sec@gmail.com
# Date: 24/11/2015
#############################################
import sys
import warnings
warnings.simplefilter("ignore")
from misp_util import *
from pymisp import PyMISP
import json

attribute2filter = {
    'ip':'ip-src&&ip-dst', 'domain':'domain&&hostname', 
    'hash':'md5&&sha1&&sha256&&malware-sample', 
    'email':'email-src&&email-dst', 'email-subject': 'email-subject'
}

if __name__ == '__main__':
    enValue = sys.argv[1]
    enType = sys.argv[0].split('_')[-1].split('2')[0] #misp_enType2event.py
    mt = MaltegoTransform()
    mt.addUIMessage("[INFO] " + enType + " to MISP Event")
    try:
        retrieveEvents(mt, attribute2filter[enType], enValue)
    except Exception as e:
        mt.addUIMessage("[Error] " + str(e))
    mt.returnOutput()

