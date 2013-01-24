# -*- coding: utf8 -*-
'''
Main server packet handler definitions.
@author: Luis Barrios Hernández
@version: 1.0
'''

from utils.enums import enum

MAIN_SERVER_PACKET_T = enum("REGISTER_VM_SERVER")

class MainServerPacketHandler(object):
    
    def __init__(self, networkManager):
        self.__packetCreator = networkManager
    
    def createVMServerRegistrationPacket(self, IPAddress, port, name):
        p = self.__packetCreator.createPacket(3)
        p.writeInt(MAIN_SERVER_PACKET_T.REGISTER_VM_SERVER)
        p.writeString(IPAddress)
        p.writeInt(port)
        p.writeString(name)
        return p
    
    
    def readPacket(self, p):
        """
        Reads the content of a virtual machine server packet
        Args:
            p: the packet with the data to read
        Returns:
            A dictionary with the packet data. The packet type will be assigned to
            the key "packet_type".
        """
        pass
        