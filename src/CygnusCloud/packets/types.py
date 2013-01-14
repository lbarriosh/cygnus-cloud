# -*- coding: utf8 -*-
'''
Packet types definitions.
@author: Luis Barrios Hernández
@version: 1.0
'''

from utils.enums import enum

VM_SERVER_PACKET_T = enum("CREATE_DOMAIN", "DOMAIN_CONNECTION_DATA", "SERVER_STATUS",
                          "USER_FRIENDLY_SHUTDOWN", "HALT")
