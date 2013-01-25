# -*- coding: utf8 -*-
'''
Main server packet handler definitions.
@author: Luis Barrios Hernández
@version: 1.0
'''

from utils.enums import enum
from database.mainServer.mainServerDB import SERVER_STATE_T

MAIN_SERVER_PACKET_T = enum("REGISTER_VM_SERVER", "VM_SERVER_REGISTRATION_ERROR", "QUERY_VM_SERVERS_STATUS",
                            "VM_SERVERS_STATUS_DATA", "UNREGISTER_OR_SHUTDOWN_VM_SERVER", "BOOTUP_VM_SERVER",
                            "VM_SERVER_BOOTUP_ERROR")


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
    
    def createDataRequestPacket(self, query):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(query)
        return p
    
    def createVMServerStatusPacket(self, segment, sequenceSize, data):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(MAIN_SERVER_PACKET_T.VM_SERVERS_STATUS_DATA)
        p.writeInt(segment)
        p.writeInt(sequenceSize)
        for row in data :
            p.writeString(row["ServerName"])
            p.writeString(row["ServerIP"])
            p.writeInt(int(row["ServerPort"]))
            p.writeString(MainServerPacketHandler.__vm_server_status_to_string(row["ServerStatus"]))
        return p
    
    def createVMServerUnregistrationOrShutdownPacket(self, serverNameOrIPAddress, halt, shutdown):
        p = self.__packetCreator.createPacket(3)
        p.writeInt(MAIN_SERVER_PACKET_T.UNREGISTER_OR_SHUTDOWN_VM_SERVER)
        p.writeString(serverNameOrIPAddress)
        p.writeBool(halt)
        p.writeBool(shutdown)
        return p
    
    def createVMServerBootUpPacket(self, serverNameOrIPAddress):
        p = self.__packetCreator.createPacket(3)
        p.writeInt(MAIN_SERVER_PACKET_T.BOOOTUP_VM_SERVER)
        p.writeString(serverNameOrIPAddress)
        return p
    
    def createVMServerBootUpErrorPacket(self, serverNameOrIPAddress, reason):
        p = self.__packetCreator.createPacket(3)
        p.writeInt(MAIN_SERVER_PACKET_T.VM_SERVER_BOOTUP_ERROR)
        p.writeString(serverNameOrIPAddress)
        p.writeString(reason)
        return p
    
    @staticmethod
    def __vm_server_status_to_string(status):
        if (status == SERVER_STATE_T.BOOTING) :
            return "Booting"
        if (status == SERVER_STATE_T.READY) :
            return "Ready"
        if (status == SERVER_STATE_T.SHUT_DOWN) :
            return "Shut down"
    
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
            
        elif (packet_type == MAIN_SERVER_PACKET_T.VM_SERVERS_STATUS_DATA) :
            result["Segment"] = p.readInt()
            result["SequenceSize"] = p.readInt()
            data = []
            while (p.hasMoreData()) :
                data.append((p.readString(), p.readString(), p.readInt(), p.readString()))
            result["Data"] = data
        
        elif (packet_type == MAIN_SERVER_PACKET_T.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
            result["ServerNameOrIPAddress"] = p.readString()
            value = p.readBool()
            result["Halt"] = value
            value = p.readBool()
            result["Shut_down"] = value
            
        elif (packet_type == MAIN_SERVER_PACKET_T.BOOOTUP_VM_SERVER) :
            result["ServerNameOrIPAddress"] = p.readString()
            
        return result
            
        