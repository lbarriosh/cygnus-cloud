# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: packetHandler.py    
    Version: 5.0
    Description: virtual machine server packet handler definitions
    
    Copyright 2012-13 Luis Barrios Hernández, Adrián Fernández Hernández,
        Samuel Guayerbas Martín

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

from virtualMachineServer.packetHandling.packet_t import VM_SERVER_PACKET_T

class VMServerPacketHandler(object):
    """
    Virtual machine server packet handler
    """
    
    def __init__(self, networkManager):
        """
        Initializes the handler's state
        Args:
            networkManager: the object that will create the network packets
        """
        self.__packetCreator = networkManager
    
    def createVMBootPacket(self, imageID, userID, commandID):
        """
        Creates a virtual machine boot packet
        Args:
            imageID: an image ID
            userID: the virtual machine owner's ID
            commandID: the virtual machine boot command's ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.CREATE_DOMAIN)
        p.writeInt(imageID)
        p.writeInt(userID)
        p.writeString(commandID)
        return p
    
    def createVMShutdownPacket(self, domainUID):
        """
        Creates a virtual machine shutdown packet
        Args:
            domainUID: the virtual machine to shutdown's ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.DESTROY_DOMAIN)
        p.writeString(domainUID)
        return p
    
    def createVMRebootPacket(self, domainUID):
        """
        Creates a virtual machine reboot packet
        Args:
            domainUID: the virtual machine to reboot's ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.REBOOT_DOMAIN)
        p.writeString(domainUID) # domainUID es el identificador del comando de arranque de la máquina. Por eso
                                # es un string.
        return p
    
    def createVMConnectionParametersPacket(self, vncServerIP, vncServerPort, password, commandID):
        """
        Creates a virtual machine connection parameters packet
        Args:
            vncServerIP: the VNC server's IPv4 address
            vncServerPort: the VNC server's port
            password: the VNC server's password
            commandID: the virtual machine boot command's ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.DOMAIN_CONNECTION_DATA)
        p.writeString(vncServerIP)
        p.writeInt(vncServerPort)
        p.writeString(password)
        p.writeString(commandID)
        return p
    
    def createVMServerDataRequestPacket(self, packet_type):
        """
        Creates a virtual machine server status request packet
        Args:
            packet_type: the packet type associated with the status request
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(7)
        p.writeInt(packet_type)
        return p
    
    def createVMServerStatusPacket(self, vmServerIP, activeDomains, ramInUse, availableRAM, freeStorageSpace, availableStorageSpace, 
                                   freeTemporarySpace, availableTemporarySpace, activeVCPUs, physicalCPUs):
        """
        Creates a virtual machine server status packet
        Args:
            vmServerIP: the virtual machine server's IP address
            activeDomains: the number of domains
            ramInUse: the used RAM amount (in kilobytes)
            availableRAM: the total RAM amount (in kilobytes)
            freeStorageSpace: the free storage space (in kilobytes)
            availableStorageSpace: the total storage space (in kilobytes)
            freeTemporarySpace: the free temporary storage space (in kilobytes)
            availableTemporarySpace: the total temporary storage space (in kilobytes)
            activeVCPUs: the number of active VCPUs
            physicalCPUs: the number of physical CPUs.
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(7)
        p.writeInt(VM_SERVER_PACKET_T.SERVER_STATUS)
        p.writeString(vmServerIP)
        p.writeInt(activeDomains)
        p.writeInt(ramInUse)
        p.writeInt(availableRAM)        
        p.writeInt(availableStorageSpace)
        p.writeInt(freeStorageSpace)
        p.writeInt(availableTemporarySpace)        
        p.writeInt(freeTemporarySpace)
        p.writeInt(activeVCPUs)
        p.writeInt(physicalCPUs)
        return p
    
    def createVMServerShutdownPacket(self, timeout=300):
        """
        Creates a virtual machine server shutdown packet
        Args:
            timeout: a timeout in seconds
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(VM_SERVER_PACKET_T.USER_FRIENDLY_SHUTDOWN)
        p.writeInt(timeout)
        return p
    
    def createVMServerHaltPacket(self):
        """
        Creates a virtual machine server immediate shutdown packet
        Args:
            None
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(VM_SERVER_PACKET_T.HALT)
        return p
    
    def createActiveVMsVNCDataPacket(self, serverIPAddress, segment, sequenceSize, data):
        """
        Creates an active VMs VNC connection data packet
        Args:
            serverIPAddress: the virtual machine server's IP address
            segment: the segment's position in the sequence
            sequenceSize: the sequence size
            data: the segment's data
        Returns:
            a packet of the specified type built from this method's arguments
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
    
    def createActiveDomainUIDsPacket(self, vmServerIP, data):
        """
        Creates a packet containing the active domain's UUIDs
        Args:
            vmServerIP: the virtual machine server's IP address
            data: a list containing the active domain's UUIDs
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.ACTIVE_DOMAIN_UIDS)
        p.writeString(vmServerIP)
        for domain_uid in data :
            p.writeString(domain_uid)
        return p
    
    def createImageEditionPacket(self, repositoryIP, repositoryPort, sourceOrTargetImageID, edit, commandID, userID):
        """
        Creates an image edition packet
        Args:
           repositoryIP: the image repository's IPv4 address
           repositoryPort: the image repository's port
           sourceOrTargetImageID: the source or target image's ID
           edit: indicates wether the image will be modified or not.
           commandID: the image edition command's ID
           userID: the image owner's ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.IMAGE_EDITION)
        p.writeString(repositoryIP)
        p.writeInt(repositoryPort)
        p.writeInt(sourceOrTargetImageID)
        p.writeBool(edit)
        p.writeString(commandID)
        p.writeInt(userID)
        return p
    
    def createErrorPacket(self, packet_type, errorDescription, commandID):
        """
        Creates an error packet
        Args:
            packet_type: the packet type associated with the error
            errorDescription: an error description code
            commandID: the command's ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(4)
        p.writeInt(packet_type)
        p.writeInt(errorDescription)
        p.writeString(commandID)
        return p
    
    def createImageDeploymentPacket(self, repositoryIP, repositoryPort, imageID, commandID):
        """
        Creates an image deployment packet
        Args:
            repositoryIP: the image repository's IPv4 address
            repositoryPort: the image repository's port
            imageID: an image ID
            commandID: the deployment command's ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.DEPLOY_IMAGE)
        p.writeString(repositoryIP)
        p.writeInt(repositoryPort)
        p.writeInt(imageID)
        p.writeString(commandID)
        return p
    
    def createDeleteImagePacket(self, imageID, commandID):
        """
        Creates an image deletion packet
        Args:
            imageID: an image ID
            commandID: the deletion command's ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.DELETE_IMAGE)
        p.writeInt(imageID)
        p.writeString(commandID)
        return p
    
    def createImageEditedPacket(self, imageID, commandID):
        """
        Creates an image edited confirmation packet
        Args:
            imageID: an image ID
            commandID: the image edition command's ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(VM_SERVER_PACKET_T.IMAGE_EDITED)
        p.writeString(commandID)
        p.writeInt(imageID)
        return p
        
    def createConfirmationPacket(self, packet_type, imageID, commandID):
        """
        Creates a confirmation packet
        Args:
            packet_type: the packet type that matches the confirmation message.
            imageID: an image ID
            commandID: the confirmed command's ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(packet_type)
        p.writeInt(imageID)
        p.writeString(commandID)
        return p
    
    def createInternalErrorPacket(self, commandID):
        """
        Creates a virtual machine server internal error packet
        Args:
            commandID: a command ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(4)
        p.writeInt(VM_SERVER_PACKET_T.INTERNAL_ERROR)
        p.writeString(commandID)
        return p
    
    def readPacket(self, p):
        """
        Reads a packet and dumps its data to a dictionary
        Args:
            p: the packet to read
        Returns:
            A dictionary with the packet's content. Its keys and values
            vary depending on the read packet's type.
        """
        result = dict()
        packet_type = p.readInt()        
        result["packet_type"] = packet_type
        (result['SenderIP'], result['SenderPort']) = p.getSenderData()
        if (packet_type == VM_SERVER_PACKET_T.CREATE_DOMAIN) :
            result["MachineID"] = p.readInt()
            result["UserID"] = p.readInt()
            result["CommandID"] = p.readString()
        elif (packet_type == VM_SERVER_PACKET_T.DESTROY_DOMAIN or 
            packet_type == VM_SERVER_PACKET_T.REBOOT_DOMAIN):
            result["DomainID"] = p.readString()
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
        elif (packet_type == VM_SERVER_PACKET_T.IMAGE_EDITION) :
            result["RepositoryIP"] = p.readString()
            result["RepositoryPort"] = p.readInt()
            result["SourceImageID"] = p.readInt()
            result["Modify"] = p.readBool()   
            result["CommandID"] = p.readString()
            result["UserID"] = p.readInt()
        elif (packet_type == VM_SERVER_PACKET_T.IMAGE_EDITION_ERROR or
              packet_type == VM_SERVER_PACKET_T.IMAGE_DEPLOYMENT_ERROR or
              packet_type == VM_SERVER_PACKET_T.IMAGE_DELETION_ERROR) :
            result["ErrorDescription"] = p.readInt()
            result["CommandID"] = p.readString()
        elif (packet_type == VM_SERVER_PACKET_T.DEPLOY_IMAGE) :
            result["RepositoryIP"] = p.readString()
            result["RepositoryPort"] = p.readInt()
            result["SourceImageID"] = p.readInt()
            result["CommandID"] = p.readString()
        elif (packet_type == VM_SERVER_PACKET_T.DELETE_IMAGE):
            result["ImageID"] = p.readInt()
            result["CommandID"] = p.readString()
        elif (packet_type == VM_SERVER_PACKET_T.IMAGE_EDITED) :
            result["CommandID"] = p.readString()
            result["ImageID"] = p.readInt()
        elif (packet_type == VM_SERVER_PACKET_T.IMAGE_DEPLOYED or
              packet_type == VM_SERVER_PACKET_T.IMAGE_DELETED):
                result["ImageID"] = p.readInt()
                result["CommandID"] = p.readString()
        elif (packet_type == VM_SERVER_PACKET_T.USER_FRIENDLY_SHUTDOWN):
            result["Timeout"] = p.readInt()
        elif (packet_type == VM_SERVER_PACKET_T.INTERNAL_ERROR) :
            result["CommandID"] = p.readString()
        # Importante: los segmentos que transportan los datos de conexión se reenviarán, por lo que no tenemos que
        # leerlos para ganar en eficiencia.
        return result