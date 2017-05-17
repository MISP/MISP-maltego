for i in misp_email2event.py misp_email-subject2event.py misp_ip2event.py misp_hash2event.py ; do ln -s -f misp_domain2event.py $i; done 
for i in misp_event2email.py misp_event2email-subject.py misp_event2hash.py misp_event2ip.py ; do ln -s -f misp_event2domain.py $i; done
