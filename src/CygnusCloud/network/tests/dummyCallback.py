# -*- coding: utf8 -*-
'''
Dummy callback object definition
@author: Luis Barrios Hernández
@version: 1.0
'''

from network.manager.networkManager import NetworkCallback

class DummyCallback(NetworkCallback):
    def processPacket(self, packet):
        print packet._serialize()
