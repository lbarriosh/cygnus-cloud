# -*- coding: utf8 -*-
'''
Main server packet handler definitions.
@author: Luis Barrios Hernández
@version: 1.0
'''

from ccutils.enums import enum
from database.clusterServer.clusterServerDB import SERVER_STATE_T

MAIN_SERVER_PACKET_T = enum("REGISTER_VM_SERVER", "VM_SERVER_REGISTRATION_ERROR", "QUERY_VM_SERVERS_STATUS",
                            "VM_SERVERS_STATUS_DATA", "QUERY_VM_DISTRIBUTION", "VM_DISTRIBUTION_DATA",
                            "UNREGISTER_OR_SHUTDOWN_VM_SERVER", "BOOTUP_VM_SERVER",
                            "VM_SERVER_BOOTUP_ERROR", "VM_BOOT_REQUEST", "VM_CONNECTION_DATA", "VM_BOOT_FAILURE", 
                            "HALT", "QUERY_ACTIVE_VM_DATA", "ACTIVE_VM_DATA")

class ClusterServerPacketHandler(object):
    """
    These objects will read and write the main server's packages.
    """    
    def __init__(self, networkManager):
        """
        Initializes the packet handler's state
        Args:
            networkManager: the networkManager object that will create the new packets
        """
        self.__packetCreator = networkManager
            
    def createVMServerRegistrationPacket(self, IPAddress, port, name):
        """
        Creates a virtual machine server registration packet
        Args:
            IPAddress: the virtual machine server's IPv4 address
            port: the virtual machine server's port
            name: the virtual machine server's desired name
        Returns:
            a new virtual machine server registration packet containing the supplied data.
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(MAIN_SERVER_PACKET_T.REGISTER_VM_SERVER)
        p.writeString(IPAddress)
        p.writeInt(port)
        p.writeString(name)
        return p
    
    def createVMRegistrationErrorPacket(self, IPAddress, port, name, reason):
        """
        Creates a virtual machine server registration error packet
        Args:
            IPAddress: the virtual machine server's IPv4 address
            port: the virtual machine server's port
            name: the virtual machine server's desired name
            reason: an error message
        Returns:
            a new virtual machine server registration error packet containing the supplied data.
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(MAIN_SERVER_PACKET_T.VM_SERVER_REGISTRATION_ERROR)
        p.writeString(IPAddress)
        p.writeInt(port)
        p.writeString(name)
        p.writeString(reason)
        return p
    
    def createDataRequestPacket(self, query):
        """
        Creates a data request packet. These packets are used to obtain a cluster's current status
        right from a cluster server.
        Args:
            query: the information we want to retrieve (i.e. active virtual machines, available images,...)
        Returns:
            a new virtual machine data request packet containing the supplied data.
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(query)
        return p
    
    def createVMServerStatusPacket(self, segment, sequenceSize, data):
        """
        Creates a virtual machine server status packet
        Args:
            segment: the packet's data sequence number
            sequenceSize: the number of segments in the sequence
            data: the packet's data
        Returns:
            a new virtual machine server status packet containing the supplied data.
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(MAIN_SERVER_PACKET_T.VM_SERVERS_STATUS_DATA)
        p.writeInt(segment)
        p.writeInt(sequenceSize)
        for row in data :
            p.writeString(row["ServerName"])
            p.writeString(ClusterServerPacketHandler.__vm_server_status_to_string(row["ServerStatus"]))
            p.writeString(row["ServerIP"])
            p.writeInt(int(row["ServerPort"]))            
        return p
    
    def createVMDistributionPacket(self, segment, sequenceSize, data):
        """
        Creates a virtual machine distribution packet
        Args:
            segment: the packet's data sequence number
            sequenceSize: the number of segments in the sequence
            data: the packet's data
        Returns:
            a new virtual machine distribution packet containing the supplied data.
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(MAIN_SERVER_PACKET_T.VM_DISTRIBUTION_DATA)
        p.writeInt(segment)
        p.writeInt(sequenceSize)
        for row in data :
            p.writeString(row["ServerName"])
            p.writeInt(row["VMID"])
        return p
    
    def createVMServerUnregistrationOrShutdownPacket(self, serverNameOrIPAddress, halt, unregister):
        """
        Creates a virtual machine server unregistration request packet
        Args:
            serverNameOrIPAddress: the virtual machine server's name or IPv4 address
            halt: True if the server must stop immediately, and false otherwise.
            unregister: True if the virtual machine server must be deleted from the cluster server's database,
            and false otherwise.
        Returns:
            a new virtual machine server unregistration request packet containing the supplied data.
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(MAIN_SERVER_PACKET_T.UNREGISTER_OR_SHUTDOWN_VM_SERVER)
        p.writeString(serverNameOrIPAddress)
        p.writeBool(halt)
        p.writeBool(unregister)
        return p
    
    def createVMServerBootUpPacket(self, serverNameOrIPAddress):
        """
        Creates a virtual machine server boot packet
        Args:
            serverNameOrIPAddress: the virtual machine server's name or IPv4 address
        Returns:
            a new virtual machine server boot packet containing the supplied data.
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(MAIN_SERVER_PACKET_T.BOOTUP_VM_SERVER)
        p.writeString(serverNameOrIPAddress)
        return p
    
    def createVMServerBootUpErrorPacket(self, serverNameOrIPAddress, reason):
        """
        Creates a virtual machine server boot up error packet
        Args:
            serverNameOrIPAddress: the virtual machine server's name or IPv4 address
            reason: an error message
        Returns:
            a new virtual machine server boot up error packet containing the supplied data.
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(MAIN_SERVER_PACKET_T.VM_SERVER_BOOTUP_ERROR)
        p.writeString(serverNameOrIPAddress)
        p.writeString(reason)
        return p
    
    def createVMBootRequestPacket(self, vmID, userID):
        """
        Creates a virtual machine boot request packet
        Args:
            vmID: the virtual machine's ID
            userID: the virtual machine user's ID
        Returns:
            a new virtual machine boot request packet containing the supplied data.
        """
        p = self.__packetCreator.createPacket(4)
        p.writeInt(MAIN_SERVER_PACKET_T.VM_BOOT_REQUEST)
        p.writeInt(vmID)
        p.writeInt(userID)
        return p
    
    def createVMBootFailurePacket(self, vmID, userID, reason):
        """
        Creates a virtual machine boot failure packet
        Args:
            vmID: the virtual machine's ID
            userID: the virtual machine user's ID
            reason: an error message
        Returns:
            a new virtual machine boot failure packet containing the supplied data.
        """
        p = self.__packetCreator.createPacket(4)
        p.writeInt(MAIN_SERVER_PACKET_T.VM_BOOT_FAILURE)
        p.writeInt(vmID)
        p.writeInt(userID)
        p.writeString(reason)
        return p
    
    def createVMConnectionDataPacket(self, userID, IPAddress, port, password):
        """
        Creates a virtual machine connection data packet
        Args:
            userID: the virtual machine user's ID
            IPAddress: the VNC server's IPv4 address
            port: the VNC server's port
            password: the VNC server's password
        Returns:
            a new virtual machine connection request packet containing the supplied data.
        """
        p = self.__packetCreator.createPacket(4)
        p.writeInt(MAIN_SERVER_PACKET_T.VM_CONNECTION_DATA)
        p.writeInt(userID)
        p.writeString(IPAddress)
        p.writeInt(port)
        p.writeString(password)
        return p
    
    def createActiveVMsDataPacket(self, packet):
        """
        Creates a VNC connection data packet
        Args:
            packet: a packet containing a VNC connection data segment.
        Returns:
            a vnc connection data packet with packet's data
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(MAIN_SERVER_PACKET_T.ACTIVE_VM_DATA)
        p.dumpData(packet)
        return p
    
    def createHaltPacket(self, haltServers):
        """
        Creates a cluster server halt packet
        Args:
            haltServers: if True, all the virtual machine servers in the cluster will kill
            their active virtual machines. If False, they'll wait until all their virtual
            machines will have been shut down.
        Returns:
            a cluster server halt packet containing the supplied data.
        """
        p = self.__packetCreator.createPacket(1)
        p.writeInt(MAIN_SERVER_PACKET_T.HALT)
        p.writeBool(haltServers)
        return p
    
    @staticmethod
    def __vm_server_status_to_string(status):
        """
        Converts the virtual machine server's status code to a human-readable string.
        Args:
            status: a virtual machine server's status code.
        Returns:
            a string with a human-readable virtual machine server status
        """
        if (status == SERVER_STATE_T.BOOTING) :
            return "Booting"
        if (status == SERVER_STATE_T.READY) :
            return "Ready"
        if (status == SERVER_STATE_T.SHUT_DOWN) :
            return "Shut down"
    
    def readPacket(self, p):
        """
        Reads the content of a cluster server packet
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
                data.append((p.readString(), p.readString(), p.readString(), p.readInt()))
            result["Data"] = data
            
        elif (packet_type == MAIN_SERVER_PACKET_T.VM_DISTRIBUTION_DATA) :
            result["Segment"] = p.readInt()
            result["SequenceSize"] = p.readInt()
            data = []
            while (p.hasMoreData()) :
                data.append((p.readString(), p.readInt()))
            result["Data"] = data
            
        elif (packet_type == MAIN_SERVER_PACKET_T.ACTIVE_VM_DATA) :
            result["Segment"] = p.readInt()
            result["SequenceSize"] = p.readInt()
            result["VMServerIP"] = p.readString()
            data = []
            while (p.hasMoreData()) :
                data.append((p.readInt(), p.readInt(), p.readString(), p.readInt(), p.readString()))
            result["Data"] = data
                
        elif (packet_type == MAIN_SERVER_PACKET_T.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
            result["ServerNameOrIPAddress"] = p.readString()
            value = p.readBool()
            result["Halt"] = value
            value = p.readBool()
            result["Unregister"] = value
            
        elif (packet_type == MAIN_SERVER_PACKET_T.BOOTUP_VM_SERVER) :
            result["ServerNameOrIPAddress"] = p.readString()
            
        elif (packet_type == MAIN_SERVER_PACKET_T.VM_SERVER_BOOTUP_ERROR) :
            result["ServerNameOrIPAddress"] = p.readString()
            result["ErrorMessage"] = p.readString()
            
        elif (packet_type == MAIN_SERVER_PACKET_T.VM_BOOT_REQUEST):
            result["VMID"] = p.readInt()
            result["UserID"] = p.readInt()
            
        elif (packet_type == MAIN_SERVER_PACKET_T.VM_BOOT_FAILURE):
            result["VMID"] = p.readInt()
            result["UserID"] = p.readInt()
            result["ErrorMessage"] = p.readString()
            
        elif (packet_type == MAIN_SERVER_PACKET_T.VM_CONNECTION_DATA):
            result["UserID"] = p.readInt()
            result["VNCServerIPAddress"] = p.readString()
            result["VNCServerPort"] = p.readInt()
            result["VNCServerPassword"] = p.readString()
            
        elif (packet_type == MAIN_SERVER_PACKET_T.HALT) :
            result["HaltVMServers"] = p.readBool()
                      
        return result