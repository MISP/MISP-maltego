# MISP-Maltego
Set of Maltego transforms to inferface with a MISP instance

# Prerequisites
- MISP instance API access
- PyMISP

# INSTALL

- Edit `misp_util.py` and set BASE_URL and API_KEY variables with your MISP base URL and MISP API key.

- Create symbolic links to `misp_domain2event.py` and `misp_event2domain.py` in the same directory.
```
for i in misp_email2event.py misp_email-subject2event.py misp_ip2event.py misp_hash2event.py ; do ln -s misp_domain2event.py $i; done
for i in misp_event2email.py misp_event2email-subject.py misp_event2hash.py misp_event2ip.py ; do ln -s misp_event2domain.py $i; done
```

- Import transforms in Maltego as follow (for instance):

  * `misp_ip2event.py`: [MISP] IP to Event / Returns MISPEvent entities containing the corresponding IP attribute
  * `misp_domain2event.py`: [MISP] Domain to Event / Returns MISPEvent entities containing the corresponding Domain attribute
  * `misp_hash2event.py`: [MISP] Hash to Event / Returns MISPEvent entities containing the corresponding Hash attribute
  * `misp_email2event.py`: [MISP] Email address to Event / Returns MISPEvent entities containing the corresponding Email address attribute
  * `misp_email-subject2event.py`: [MISP] Email subject to Event / Returns MISPEvent entities containing the corresponding Email subject attribute
  * `misp_event2ip.py`: [MISP] Event to IP attribute / Returns the IP attributes belonging to an event
  * `misp_event2domain.py`: [MISP] Event to Domain attribute / Returns Domain attributes belonging to an event
  * `misp_event2hash.py`: [MISP] Event to Hash attribute / Returns Hash attributes belonging to an event
  * `misp_event2email.py`: [MISP] Event to Email address attribute / Returns Email address attributes belonging to an event
  * `misp_event2email-subject.py`: [MISP] Event to Email subject attribute / Returns Email subject attributes belonging to an event
  * `misp_getEventInfo.py`: [MISP] Get Event Info / Adorns the Event with Info as notes
