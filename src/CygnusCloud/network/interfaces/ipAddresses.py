# -*- coding: utf8 -*-
'''

Interface IP address finder

@author: Paul Cannon (ActiveState code recipes)
'''


import socket

import fcntl

import struct


def get_ip_address(ifname):

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    return socket.inet_ntoa(fcntl.ioctl(

        s.fileno(),

        0x8915,  # SIOCGIFADDR

        struct.pack('256s', ifname[:15])

    )[20:24])


if __name__ == "__main__" :

    print get_ip_address('eth0')