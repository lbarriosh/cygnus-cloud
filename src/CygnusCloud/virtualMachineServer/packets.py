# -*- coding: utf8 -*-
'''
Virtual machine server packet handler definitions.
@author: Luis Barrios Hernández
@version: 2.0
'''

from utils.enums import enum

VM_SERVER_PACKET_T = enum("CREATE_DOMAIN", "DOMAIN_CONNECTION_DATA", "SERVER_STATUS",
                          "SERVER_STATUS_REQUEST", "USER_FRIENDLY_SHUTDOWN", "HALT")

class VMServerPacketHandler(object):
    
    def __init__(self, networkManager):
        self.__packetCreator = networkManager
    
    def createVMBootPacket(self, machineId, userId):
        """
        Creates a virtual machine boot packet
        Args:
            machineId: the virtual machine to boot unique identifier
            userId: the unique identifier of the user that requested
            the virtual machine to boot.
        Returns:
            A packet with the specified data.
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.CREATE_DOMAIN)
        p.writeLong(machineId)
        p.writeLong(userId)
        return p
    
    def createVMConnectionParametersPacket(self, vncServerIP, vncServerPort, password):
        """
        Creates a virtual machine connection parameters packet
        Args:
            vncServerIP: the VNC server's IP address
            vncServerPort: the VNC server's port
            password: the VNC server's password
        Returns:
            A packet with the specified data
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.DOMAIN_CONNECTION_DATA)
        p.writeString(vncServerIP)
        p.writeInt(vncServerPort)
        p.writeString(password)
        return p
    
    def createVMServerStatusRequestPacket(self):
        p = self.__packetCreator.createPacket(7)
        p.writeInt(VM_SERVER_PACKET_T.SERVER_STATUS_REQUEST)
        return p
    
    def createVMServerStatusPacket(self, vncServerIP, activeDomains):
        """
        Creates a virtual machine server status packet
        Args:
            vncServerIP: the VNC server's IP address
            activeDomains: the number of virtual machines that are currently running
            on the server.
        Returns:
            A packet with the specified data
        """
        p = self.__packetCreator.createPacket(7)
        p.writeInt(VM_SERVER_PACKET_T.SERVER_STATUS)
        p.writeString(vncServerIP)
        p.writeInt(activeDomains)
        return p
    
    def createVMServerShutdownPacket(self):
        """
        Creates a virtual machine server soft shutdown packet
        Args:
            None
        Returns:
            A packet with the specified data
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(VM_SERVER_PACKET_T.USER_FRIENDLY_SHUTDOWN)
        return p
    
    def createVMServerHaltPacket(self):
        """
        Creates a virtual machine server halt packet
        Args:
            None
        Returns:
            A packet with the specified data
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(VM_SERVER_PACKET_T.USER_FRIENDLY_SHUTDOWN)
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
        if (packet_type == VM_SERVER_PACKET_T.CREATE_DOMAIN) :
            result["machineId"] = p.readLong()
            result["userId"] = p.readLong()
        if (packet_type == VM_SERVER_PACKET_T.DOMAIN_CONNECTION_DATA):
            result["VNCServerIP"] = p.readString()
            result["VNCServerPort"] = p.readInt()
            result["VNCServerPassword"] = p.readString()
        if (packet_type == VM_SERVER_PACKET_T.SERVER_STATUS) :
            result["VNCServerIP"] = p.readString()
            result["ActiveDomains"] = p.readInt()
        if (packet_type == VM_SERVER_PACKET_T.USER_FRIENDLY_SHUTDOWN or\
            packet_type == VM_SERVER_PACKET_T.HALT or \
            packet_type == VM_SERVER_PACKET_T.SERVER_STATUS_REQUEST):
           pass
        return result
        