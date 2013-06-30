# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: packetHandler.py    
    Version: 5.0
    Description: cluster server packet handler definition
    
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
from clusterServer.packetHandling.packet_t import CLUSTER_SERVER_PACKET_T

class ClusterServerPacketHandler(object):
    """
    Cluster server packet handler
    """    
    def __init__(self, networkManager):
        """
        Initializes the packet handler's state
        Args:
            networkManager: the object that will create the network packets
        """
        self.__packetCreator = networkManager
        
    def createErrorPacket(self, packet_type, errorDescription, commandID):
        """
        Creates an error packet
        Args:
            packet_type: the packet type associated with the error
            errorDescription: the error description code
            commandID: a commandID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(packet_type)
        p.writeInt(errorDescription)
        p.writeString(commandID)
        return p
        
    def createAutoDeployPacket(self, imageID, instances, commandID):
        """
        Creates an image auto-deployment packet
        Args:
            imageID: the affected image's ID
            instances: the number of new instances to be hosted
            commandID: a commandID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(4)
        p.writeInt(CLUSTER_SERVER_PACKET_T.AUTO_DEPLOY)
        p.writeInt(imageID)
        p.writeInt(instances)
        p.writeString(commandID)
        return p
            
    def createVMServerRegistrationPacket(self, IPAddress, port, name, isEditionServer, commandID):
        """
        Creates a virtual machine server registration packet
        Args:
            IPAddress: the virtual machine server's IP address
            port: the virtual machine server's port
            name: the virtual machine server's name
            isEditionServer: indicates if the virtual machine server will be used to create and edit 
                images or not
            commandID: a command ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(4)
        p.writeInt(CLUSTER_SERVER_PACKET_T.REGISTER_VM_SERVER)
        p.writeString(IPAddress)
        p.writeInt(port)
        p.writeString(name)
        p.writeBool(isEditionServer)
        p.writeString(commandID)
        return p
    
    def createCommandExecutedPacket(self, commandID):
        """
        Creates a command executed packet
        Args:
            commandID: the executed command's ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(CLUSTER_SERVER_PACKET_T.COMMAND_EXECUTED)
        p.writeString(commandID)
        return p  
    
    def createImageEditedPacket(self, commandID, imageID):  
        """
        Creates an image edited packet
        Args:
            commandID: the image edition command's ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(CLUSTER_SERVER_PACKET_T.IMAGE_CREATED)
        p.writeString(commandID)
        p.writeInt(imageID)
        return p  
    
    def createDataRequestPacket(self, packet_type):
        """
        Creates a data request packet
        Args:
            packet_type: the packet type associated with the query to execute in the cluster server
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(10)
        p.writeInt(packet_type)
        return p
    
    def createVMServerStatusPacket(self, segment, sequenceSize, data):
        """
        Creates a virtual machine serverstatus packet
        Args:
            segment: the segment's position in the sequence
            sequenceSize: the number of segments in the sequence
            data: the segment's data
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(10)
        p.writeInt(CLUSTER_SERVER_PACKET_T.VM_SERVERS_STATUS_DATA)
        p.writeInt(segment)
        p.writeInt(sequenceSize)
        for row in data :
            p.writeString(row["ServerName"])
            p.writeInt(row["ServerStatus"])
            p.writeString(row["ServerIP"])
            p.writeInt(int(row["ServerPort"]))   
            p.writeBool(int(row["IsEditionServer"]) == 1)         
        return p
    
    def createVMDistributionPacket(self, segment, sequenceSize, data):
        """
        Creates a virtual machine distribution packet
        Args:
            segment: the segment's position in the sequence
            sequenceSize: the number of segments in the sequence
            data: the segment's data
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(CLUSTER_SERVER_PACKET_T.VM_DISTRIBUTION_DATA)
        p.writeInt(segment)
        p.writeInt(sequenceSize)
        for row in data :
            p.writeString(row["ServerName"])
            p.writeInt(row["ImageID"])
            p.writeInt(row["CopyStatus"])
        return p
    
    def createVMServerUnregistrationOrShutdownPacket(self, serverNameOrIPAddress, isShutDown, unregister, commandID):
        """
        Creates a virtual machine server unregistration or shutdown packet
        Args:
            serverNameOrIPAddress: the virtual machine server's name or IPv4 address
            isShutDown: indicates if the virtual machine server must be shut down
            unregister: indicates if the virtual machine server must be unregistered
            commandID: a command ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(CLUSTER_SERVER_PACKET_T.UNREGISTER_OR_SHUTDOWN_VM_SERVER)
        p.writeString(serverNameOrIPAddress)
        p.writeBool(isShutDown)
        p.writeBool(unregister)
        p.writeString(commandID)
        return p
    
    def createVMServerBootPacket(self, serverNameOrIPAddress, commandID):
        """
        Creates a virtual machine server boot packet
        Args:
            serverNameOrIPAddress: the virtual machine server's name or IPv4 address
            commandID: a command ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(4)
        p.writeInt(CLUSTER_SERVER_PACKET_T.BOOTUP_VM_SERVER)
        p.writeString(serverNameOrIPAddress)
        p.writeString(commandID)
        return p
    
    def createVMBootRequestPacket(self, imageID, userID, commandID):
        """
        Creates a virtual machine boot request packet
        Args:
            imageID: an image ID
            userID: the virtual machine owner's ID
            commandID: a command ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(CLUSTER_SERVER_PACKET_T.VM_BOOT_REQUEST)
        p.writeInt(imageID)
        p.writeInt(userID)
        p.writeString(commandID)
        return p
    
    def createVMConnectionDataPacket(self, IPAddress, port, password, commandID):
        """
        Creates a virtual machine connection data packet
        Args:
            IPAddress: the VNC server's IP address
            port: the VNC server's port
            password: the VNC server's password
            commandID: a commandID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(CLUSTER_SERVER_PACKET_T.VM_CONNECTION_DATA)
        p.writeString(IPAddress)
        p.writeInt(port)
        p.writeString(password)
        p.writeString(commandID)
        return p
    
    def createActiveVMsVNCDataPacket(self, data):
        """
        Creates an active virtual machines VNC data packet
        Args:
            data: a string with the data to send
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(10)
        p.writeInt(CLUSTER_SERVER_PACKET_T.ACTIVE_VM_VNC_DATA)
        p.dumpData(data)
        return p
    
    def createHaltPacket(self, haltServers):
        """
        Creates a halt packet
        Args:
            haltServers: indicates if the virtual machine servers must be shut down immediately or not
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(1)
        p.writeInt(CLUSTER_SERVER_PACKET_T.HALT)
        p.writeBool(haltServers)
        return p
    
    def createDomainDestructionPacket(self, domainID, commandID):
        """
        Creates a domain destruction packet
        Args:
            domainID: the domain to be destructed ID
            commandID: a command ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(CLUSTER_SERVER_PACKET_T.DOMAIN_DESTRUCTION)
        p.writeString(domainID)
        p.writeString(commandID)
        return p
    
    def createDomainRebootPacket(self, domainID, commandID):
        """
        Creates a domain reboot packet
        Args:
            domainID: the domain to be rebooted ID
            commandID: a command ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5) 
        p.writeInt(CLUSTER_SERVER_PACKET_T.DOMAIN_REBOOT)
        p.writeString(domainID)
        p.writeString(commandID)
        return p
    
    def createRepositoryStatusPacket(self, freeDiskSpace, availableDiskSpace, status):
        """
        Creates an image repository status packet
        Args:
            freeDiskSpace: the free disk space in the image repository
            availableDiskSpace: the total disk space in the image repository
            status: the image repository connection status
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(10)
        p.writeInt(CLUSTER_SERVER_PACKET_T.REPOSITORY_STATUS)
        p.writeInt(freeDiskSpace)
        p.writeInt(availableDiskSpace)
        p.writeInt(status)
        return p
        
    def createVMServerConfigurationChangePacket(self, serverNameOrIPAddress, newName, newIPAddress, newPort, newImageEditionBehavior, commandID):
        """
        Creates a virtual machine server configuration change packet
        Args:
            serverNameOrIPAddress: the virtual machine server's name or IP address
            newName: the virtual machine server's new name
            newIPAddress: the virtual machine server's IP new address
            newPort: the virtual machine server's new port            
            newImageEditionBehavior: indicates if the virtual machine server will be used to create and edit 
                images or not
            commandID: a command ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(4)
        p.writeInt(CLUSTER_SERVER_PACKET_T.VM_SERVER_CONFIGURATION_CHANGE)
        p.writeString(serverNameOrIPAddress)
        p.writeString(newName)
        p.writeString(newIPAddress)
        p.writeInt(newPort)
        p.writeBool(newImageEditionBehavior)
        p.writeString(commandID)
        return p
        
    def createImageDeploymentPacket(self, packet_type, serverNameOrIPAddress, imageID, commandID):
        """
        Creates an image deployment packet
        Args:
            packet_type: the packet type associated with the operation
            serverNameOrIPAddress: the affected virtual machien server's IP address
            imageID: the affected image's ID
            commandID: a command ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(packet_type)    
        p.writeString(serverNameOrIPAddress)    
        p.writeInt(imageID)
        p.writeString(commandID)
        return p
    
    def createImageEditionPacket(self, packet_type, imageID, ownerID, commandID):
        """
        Creates an image edition packet
        Args:
            packet_type: the packet type associated with the operation
            serverNameOrIPAddress: the affected virtual machien server's IP address
            imageID: the affected image's ID
            ownerID: the new virtual machine owner's ID
            commandID: a command ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(packet_type)
        p.writeInt(imageID)
        p.writeInt(ownerID)
        p.writeString(commandID)
        return p
    
    def createFullImageDeletionPacket(self, imageID, commandID):
        """
        Creates a full image deletion packet
        Args:
            imageID: the affected image's ID
            commandID: a commandID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(4)
        p.writeInt(CLUSTER_SERVER_PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE)
        p.writeInt(imageID)
        p.writeString(commandID)
        return p
    
    def createVMServerResourceUsagePacket(self, segment, sequenceSize, data):
        """
        Creates a virtual machine server resource usage packet
        Args:
            segment: the segment's position in the sequence
            sequenceSize: the number of segments in the sequence
            data: the segment's data
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(CLUSTER_SERVER_PACKET_T.VM_SERVERS_RESOURCE_USAGE)
        p.writeInt(segment)
        p.writeInt(sequenceSize)
        for row in data :
            p.writeString(row["ServerName"])
            p.writeInt(row["ActiveHosts"])
            p.writeInt(row["RAMInUse"])
            p.writeInt(row["RAMSize"])
            p.writeInt(row["FreeStorageSpace"])
            p.writeInt(row["AvailableStorageSpace"])
            p.writeInt(row["FreeTemporarySpace"])
            p.writeInt(row["AvailableTemporarySpace"])
            p.writeInt(row["ActiveVCPUs"])
            p.writeInt(row["PhysicalCPUs"])
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
        if (packet_type == CLUSTER_SERVER_PACKET_T.REGISTER_VM_SERVER) :
            result["VMServerIP"] = p.readString()
            result["VMServerPort"] = p.readInt()
            result["VMServerName"] = p.readString()
            result["IsEditionServer"] = p.readBool()
            result["CommandID"] = p.readString()        
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVERS_STATUS_DATA) :
            result["Segment"] = p.readInt()
            result["SequenceSize"] = p.readInt()
            data = []
            while (p.hasMoreData()) :
                data.append((p.readString(), p.readInt(), p.readString(), p.readInt(), p.readBool()))
            result["Data"] = data
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.VM_DISTRIBUTION_DATA) :
            result["Segment"] = p.readInt()
            result["SequenceSize"] = p.readInt()
            data = []
            while (p.hasMoreData()) :
                data.append((p.readString(), p.readInt(), p.readInt()))
            result["Data"] = data
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.ACTIVE_VM_VNC_DATA) :
            result["Segment"] = p.readInt()
            result["SequenceSize"] = p.readInt()
            result["VMServerIP"] = p.readString()
            data = []
            while (p.hasMoreData()) :
                data.append((p.readString(), p.readInt(), p.readInt(), p.readString(), p.readInt(), p.readString()))
            result["Data"] = data
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVERS_RESOURCE_USAGE):
            result["Segment"] = p.readInt()
            result["SequenceSize"] = p.readInt()
            data = []
            while (p.hasMoreData()) :
                data.append((p.readString(), p.readInt(), p.readInt(), p.readInt(), p.readInt(), p.readInt(), p.readInt(), p.readInt(), p.readInt(), p.readInt()))
            result["Data"] = data
                
        elif (packet_type == CLUSTER_SERVER_PACKET_T.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
            result["ServerNameOrIPAddress"] = p.readString()
            result["Halt"] =  p.readBool()
            result["Unregister"] = p.readBool()
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.BOOTUP_VM_SERVER) :
            result["ServerNameOrIPAddress"] = p.readString()
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.DEPLOY_IMAGE or
              packet_type == CLUSTER_SERVER_PACKET_T.DELETE_IMAGE_FROM_SERVER) :
            result["ServerNameOrIPAddress"] = p.readString()
            result["ImageID"] = p.readInt()
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.VM_BOOT_REQUEST):
            result["VMID"] = p.readInt()
            result["UserID"] = p.readInt()
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.VM_CONNECTION_DATA):
            result["VNCServerIPAddress"] = p.readString()
            result["VNCServerPort"] = p.readInt()
            result["VNCServerPassword"] = p.readString()
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.HALT) :
            result["HaltVMServers"] = p.readBool()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.COMMAND_EXECUTED) :
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.DOMAIN_DESTRUCTION or
              packet_type == CLUSTER_SERVER_PACKET_T.DOMAIN_REBOOT) :
            result["DomainID"] = p.readString()
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVER_CONFIGURATION_CHANGE): 
            result["ServerNameOrIPAddress"] = p.readString()    
            result["NewVMServerName"] = p.readString()
            result["NewVMServerIPAddress"] = p.readString()
            result["NewVMServerPort"] = p.readInt()
            result["NewImageEditionBehavior"] = p.readBool()
            result["CommandID"] = p.readString() 
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.REPOSITORY_STATUS) :
            result["FreeDiskSpace"] = p.readInt()
            result["AvailableDiskSpace"] = p.readInt()
            result["RepositoryStatus"] = p.readInt()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.CREATE_IMAGE or 
              packet_type == CLUSTER_SERVER_PACKET_T.EDIT_IMAGE):
            result["ImageID"] = p.readInt()
            result["OwnerID"] = p.readInt()
            result["CommandID"] = p.readString() 
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE) :
            result["ImageID"] = p.readInt()
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.AUTO_DEPLOY):
            result["ImageID"] = p.readInt()
            result["Instances"] = p.readInt()
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.IMAGE_CREATED):
            result["CommandID"] = p.readString()
            result["ImageID"] = p.readInt()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVER_REGISTRATION_ERROR or 
              packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVER_BOOTUP_ERROR or 
              packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVER_UNREGISTRATION_ERROR or 
              packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVER_SHUTDOWN_ERROR or
              packet_type == CLUSTER_SERVER_PACKET_T.IMAGE_DEPLOYMENT_ERROR or
              packet_type == CLUSTER_SERVER_PACKET_T.DELETE_IMAGE_FROM_SERVER_ERROR or 
              packet_type == CLUSTER_SERVER_PACKET_T.VM_BOOT_FAILURE or 
              packet_type == CLUSTER_SERVER_PACKET_T.DOMAIN_DESTRUCTION_ERROR or
              packet_type == CLUSTER_SERVER_PACKET_T.DOMAIN_REBOOT_ERROR or
              packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVER_CONFIGURATION_CHANGE_ERROR or 
              packet_type == CLUSTER_SERVER_PACKET_T.IMAGE_CREATION_ERROR or
              packet_type == CLUSTER_SERVER_PACKET_T.IMAGE_EDITION_ERROR or
              packet_type == CLUSTER_SERVER_PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR or
              packet_type == CLUSTER_SERVER_PACKET_T.AUTO_DEPLOY_ERROR or
              packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVER_INTERNAL_ERROR) :
            result["ErrorDescription"] = p.readInt()        
            result["CommandID"] = p.readString()                       
        return result