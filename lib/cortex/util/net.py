""" cortex.util.net
"""

import socket

from cortex.core.data import LOOPBACK_HOST

def is_open(port, ip=LOOPBACK_HOST):
    """ answers whether port@ip is up or down.
        this probably doesn't work everywhere..
        but would you prefer i use nmap?
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False

def ipaddr_with_internet():
    """ you need to make an outbound connection to get
        an ip-address on a particular interface.. this
        function requires interwebs
    """
    port = 80
    host = "gmail.com"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((host, port))
    return s.getsockname()

def ipaddr_hosts():
    """ on linux, uses /etc/hosts, returns something like this:

         ('cormac', ['localhost', 'testserver'], ['127.0.0.1'])
    """
    name, aliaslist, addresslist = socket.gethostbyname_ex(socket.gethostname())
    return name, aliaslist, addresslist

def ipaddr_basic():
    """ two different approaches just for reference purposes..
        these results are always the same for me, but ymmv depending
        on setup and platform..
    """
    x = []
    x.append(socket.gethostbyname(socket.gethostname()))
    x.append(socket.gethostbyname(socket.getfqdn()))
    return set(map(str, x))
