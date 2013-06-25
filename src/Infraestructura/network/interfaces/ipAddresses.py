# -*- coding: utf8 -*-
'''   
    File: ipAddresses.py    
    Version: 1.0
    Description: network interface IP addresses finder
    
    Copyright 2005 Paul Cannon
        
    Licensed under the Python License, version 2. You can download a copy from
    
            http://opensource.org/licenses/Python-2.0
'''

import socket
import fcntl
import struct

def get_ip_address(interfaceName):
    """
    Returns a network interface's IPv4 address
    Args:
        interfaceName: the network interface's name
    Returns:
        the network interface's IPv4 address
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s', interfaceName[:15])
    )[20:24])