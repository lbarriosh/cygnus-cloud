# -*- coding: utf8 -*-
'''
Virtual machine server packet handler definitions.
@author: Luis Barrios Hernández
@version: 2.1
'''

from ccutils.enums import enum

VM_SERVER_PACKET_T = enum("CREATE_DOMAIN", "DESTROY_DOMAIN", "DOMAIN_CONNECTION_DATA", "SERVER_STATUS",
                          "SERVER_STATUS_REQUEST", "USER_FRIENDLY_SHUTDOWN", 
                          "QUERY_ACTIVE_VM_DATA", "ACTIVE_VM_DATA", "HALT", "QUERY_ACTIVE_DOMAIN_UIDS", "ACTIVE_DOMAIN_UIDS",
                          "REQUEST_DOWNLOAD_SLOT", "REQUEST_UPLOAD_SLOT")

class VMServerPacketHandler(object):
    
    def __init__(self, networkManager):
        self.__packetCreator = networkManager
    
    def createVMBootPacket(self, machineId, userId, commandID):
        """
        Creates a virtual machine boot packet
        Args:
            machineId: the virtual machine to boot unique identifier
            userId: the unique identifier of the user that requested
            the virtual machine to boot.
            commandID: the boot command's unique identifier
        Returns:
            A packet with the specified data.
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.CREATE_DOMAIN)
        p.writeInt(machineId)
        p.writeInt(userId)
        p.writeString(commandID)
        return p
    
    def createVMShutdownPacket(self, vmID):
        """
        Crea un paquete para apagar una máquina virtual
        Args:
            vmID: el identificador único de la máquina virtual
        Returns:
            Un paquete que contiene los datos especificados
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.DESTROY_DOMAIN)
        p.writeString(vmID) # vmID es el identificador del comando de arranque de la máquina. Por eso
                            # es un string.
        return p
    
    def createVMConnectionParametersPacket(self, vncServerIP, vncServerPort, password, commandID):
        """
        Creates a virtual machine connection parameters packet
        Args:
            vncServerIP: the VNC server's IP address
            vncServerPort: the VNC server's port
            password: the VNC server's password
            commandID: the boot command's unique identifier
        Returns:
            A packet with the specified data
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.DOMAIN_CONNECTION_DATA)
        p.writeString(vncServerIP)
        p.writeInt(vncServerPort)
        p.writeString(password)
        p.writeString(commandID)
        return p
    
    def createVMServerDataRequestPacket(self, packet_type):
        p = self.__packetCreator.createPacket(7)
        p.writeInt(packet_type)
        return p
    
    def createVMServerStatusPacket(self, vncServerIP, activeDomains, ramInUse, availableRAM, freeStorageSpace, availableStorageSpace, 
                                   freeTemporarySpace, availableTemporarySpace, activeVCPUs, realCPUs):
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
        p.writeInt(ramInUse)
        p.writeInt(availableRAM)
        p.writeInt(freeStorageSpace)
        p.writeInt(availableStorageSpace)
        p.writeInt(freeTemporarySpace)
        p.writeInt(availableTemporarySpace)
        p.writeInt(activeVCPUs)
        p.writeInt(realCPUs)
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
        p.writeInt(VM_SERVER_PACKET_T.HALT)
        return p
    
    def createActiveVMsDataPacket(self, serverIPAddress, segment, sequenceSize, data):
        """
        Creates an active virtual machines data data
        Args:
            serverIPAddress: the VNC server's IPv4 address
            segment: the data's segment number
            sequenceSize: the total number of data segments
            data: the segment's data
        """
        p = self.__packetCreator.createPacket(6)
        p.writeInt(VM_SERVER_PACKET_T.ACTIVE_VM_DATA)
        p.writeInt(segment)
        p.writeInt(sequenceSize)
        p.writeString(serverIPAddress)
        for row in data :
            p.writeString(row["DomainID"])
            p.writeInt(row["UserID"])
            p.writeInt(row["ImageID"])
            p.writeString(row["VMName"])
            p.writeInt(row["VNCPort"])
            p.writeString(row["VNCPass"])
        return p    
    
    def createActiveDomainUIDsPacket(self, vncServerIP, data):
        """
        Crea un paquete que contiene los identificadores únicos de todas las máquinas virtuales
        Argumentos:
            vncServerIP: la dirección IP del servidor VNC. Se usará para identificar de forma única a este servidor
            data: lista con los identificadores únicos de las máquinas virtuales
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.ACTIVE_DOMAIN_UIDS)
        p.writeString(vncServerIP)
        for domain_uid in data :
            p.writeString(domain_uid)
        return p
    
    def createRequestDownloadSlotPacket(self, serverIP, port, requestID):
        """
        Crea un paquete para pedir un hueco al repositorio para bajarse un imagen
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.REQUEST_DOWNLOAD_SLOT)
        p.writeString(serverIP)
        p.writeInt(port)
        p.writeInt(requestID)
        return p
    
    def createRequestUploadSlotPacket(self, serverIP, port, requestID):
        """
        Crea un paquete para pedir un hueco al repositorio para subir una imagen
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.REQUEST_UPLOAD_SLOT)
        p.writeString(serverIP)
        p.writeInt(port)
        p.writeInt(requestID)
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
            result["MachineID"] = p.readInt()
            result["UserID"] = p.readInt()
            result["CommandID"] = p.readString()
        elif (packet_type == VM_SERVER_PACKET_T.DESTROY_DOMAIN) :
            result["VMID"] = p.readString()
        elif (packet_type == VM_SERVER_PACKET_T.DOMAIN_CONNECTION_DATA):
            result["VNCServerIP"] = p.readString()
            result["VNCServerPort"] = p.readInt()
            result["VNCServerPassword"] = p.readString()
            result["CommandID"] = p.readString()
        elif (packet_type == VM_SERVER_PACKET_T.SERVER_STATUS and p.hasMoreData()) :
            result["VMServerIP"] = p.readString()
            result["ActiveDomains"] = p.readInt()
            result["RAMInUse"] = p.readInt()
            result["RAMSize"] = p.readInt()
            result["FreeStorageSpace"] = p.readInt()
            result["AvailableStorageSpace"] = p.readInt()
            result["FreeTemporarySpace"] = p.readInt()
            result["AvailableTemporarySpace"] = p.readInt()
            result["ActiveVCPUs"] = p.readInt()
            result["PhysicalCPUs"] = p.readInt()
        elif (packet_type == VM_SERVER_PACKET_T.ACTIVE_DOMAIN_UIDS) :
            ac = []
            result["VMServerIP"] = p.readString()
            while (p.hasMoreData()):
                ac.append(p.readString())
            result["Domain_UIDs"] = ac
        elif (packet_type == VM_SERVER_PACKET_T.REQUEST_DOWNLOAD_SLOT or
              packet_type == VM_SERVER_PACKET_T.REQUEST_UPLOAD_SLOT) :
            result["IP"] = p.readString()
            result["port"] = p.readInt()
            result["requestID"] = p.readInt()
        
        # Note that the connection data segments will be sent to the web server immediately.
        # Therefore, they don't need to be read in the main server or in the virtual machine server.        
        return result