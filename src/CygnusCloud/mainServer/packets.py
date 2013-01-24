# -*- coding: utf8 -*-
'''
Main server packet handler definitions.
@author: Luis Barrios Hernández
@version: 1.0
'''

from utils.enums import enum

MAIN_SERVER_PACKET_T = enum("REGISTER_VM_SERVER", "VM_SERVER_REGISTRATION_ERROR")

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
    
    def createVMRegistrationErrorPacket(self, IPAddress, port, name, reason):
        p = self.__packetCreator.createPacket(3)
        p.writeInt(MAIN_SERVER_PACKET_T.VM_SERVER_REGISTRATION_ERROR)
        p.writeString(IPAddress)
        p.writeInt(port)
        p.writeString(name)
        p.writeString(reason)
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
        result = dict()
        packet_type = p.readInt()
        result["packet_type"] = packet_type
        if (packet_type == MAIN_SERVER_PACKET_T.REGISTER_VM_SERVER) :
            result["VMServerIP"] = p.readString()
            result["VMServerPort"] = p.readInt()
            result["VMServerName"] = p.readString()
        elif (packet_type == MAIN_SERVER_PACKET_T.VM_SERVER_REGISTRATION_ERROR) :
            result["VMServerIP"] = p.readString()
            result["VMServerPort"] = p.readInt()
            result["VMServerName"] = p.readString()
            result["ErrorMessage"] = p.readString()
            
        return result
            
        