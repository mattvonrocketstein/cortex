""" """
import nmap
nm = nmap.PortScanner()
nm.scan('127.0.0.1', '22-443')
nm.command_line()
#u'nmap -oX - -p 22-443 -sV 127.0.0.1'
nm.scaninfo()
#{u'tcp': {'services': u'22-443', 'method': u'connect'}}
nm.all_hosts()
#[u'127.0.0.1']
nm['127.0.0.1'].hostname()
#u'localhost'
nm['127.0.0.1'].state()
#u'up'
nm['127.0.0.1'].all_protocols()
#[u'tcp']
nm['127.0.0.1']['tcp'].keys()
#[80, 25, 443, 22, 111]
nm['127.0.0.1'].has_tcp(22)
True
nm['127.0.0.1'].has_tcp(23)
False
nm['127.0.0.1']['tcp'][22]
{'state': u'open', 'reason': u'syn-ack', 'name': u'ssh'}
nm['127.0.0.1'].tcp(22)
{'state': u'open', 'reason': u'syn-ack', 'name': u'ssh'}
nm['127.0.0.1']['tcp'][22]['state']
u'open'

for host in nm.all_hosts():
    print('----------------------------------------------------')
    print('Host : %s (%s)' % (host, nm[host].hostname()))
    print('State : %s' % nm[host].state())
    for proto in nm[host].all_protocols():
        print('----------')
        print('Protocol : %s' % proto)

        lport = nm[host][proto].keys()
        lport.sort()
        for port in lport:
            print ('port : %s\tstate : %s' % (port, nm[host][proto][port]['state']))
