# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: endpointPacketReactor.py    
    Version: 5.0
    Description: cluster endpoint packet reactor definition
    
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

from clusterServer.packetHandling.packet_t import CLUSTER_SERVER_PACKET_T as PACKET_T
from network.manager.networkManager import NetworkManager
from errors.codes import ERROR_DESC_T
from time import sleep
from clusterServer.loadBalancing.loadBalancer import MODE_T
from clusterServer.loadBalancing.penaltyBasedLoadBalancer import PenaltyBasedLoadBalancer
from clusterServer.database.server_state_t import SERVER_STATE_T
from clusterServer.database.image_state_t import IMAGE_STATE_T
from virtualMachineServer.packetHandling.packet_t import VM_SERVER_PACKET_T as VMSRVR_PACKET_T

class EndpointPacketReactor(object):
    """
    These objects process the packets sent from the cluster endpoint
    """
    def __init__(self, dbConnector, networkManager, vmServerPacketHandler, clusterServerPacketHandler, imageRepositoryPacketHandler,
                 vmServerCallback, listenningPort, repositoryIP, repositoryPort, loadBalancerSettings, 
                 averageCompressionRatio, useSSL):
        """
        Initializes the reactor's state
        Args:
            dbConnector: a cluster server database connector
            networkManager: the network manager to use
            vmServerPacketHandler: the virtual machine server packet handler
            clusterServerPacketHandler: the cluster server packet handler
            imageRepositoryPacketHandler: the image repository packet handler
            vmServerCallback: the virtual machine server packet reactor
            listenningPort: the control connection's listenning port
            repositoryIP: the image repository's IP address
            repositoryPort: the image repository's port
            loadBalancerSettings: the load balancing algorithm settings 
            averageCompressionRatio: the compression algorithm's average compression ratio
            useSSL: indicates if the network connections use SSL encryption or not
        """
        self.__commandsDBConnector = dbConnector
        self.__networkManager = networkManager
        self.__vmServerPacketHandler = vmServerPacketHandler
        self.__packetHandler = clusterServerPacketHandler
        self.__imageRepositoryPacketHandler = imageRepositoryPacketHandler
        self.__loadBalancer = PenaltyBasedLoadBalancer(self.__commandsDBConnector, loadBalancerSettings[1], 
            loadBalancerSettings[2], loadBalancerSettings[3], loadBalancerSettings[4], 
            loadBalancerSettings[5])
        self.__averageCompressionRatio = averageCompressionRatio
        self.__vmServerCallback = vmServerCallback
        self.__listenningPort = listenningPort
        self.__repositoryIP = repositoryIP
        self.__repositoryPort = repositoryPort
        self.__finished = False
        self.__useSSL = useSSL
    
    def processClusterEndpointIncomingPacket(self, packet):
        """
        Processes a packet sent from the cluster endpoint
        Args:
            packet: the packet to process
        Returns:
            Nothing
        """
        data = self.__packetHandler.readPacket(packet)
        if (data["packet_type"] == PACKET_T.REGISTER_VM_SERVER) :
            self.__registerVMServer(data)
        elif (data["packet_type"] == PACKET_T.QUERY_VM_SERVERS_STATUS) :
            self.__sendStatusData(self.__commandsDBConnector.getVMServerConfiguration, self.__packetHandler.createVMServerStatusPacket)
        elif (data["packet_type"] == PACKET_T.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
            self.__unregisterOrShutdownVMServer(data)
        elif (data["packet_type"] == PACKET_T.BOOTUP_VM_SERVER) :
            self.__bootVMServer(data)
        elif (data["packet_type"] == PACKET_T.VM_BOOT_REQUEST):
            self.__bootVM(data)
        elif (data["packet_type"] == PACKET_T.HALT) :
            self.__doImmediateShutdown(data)
        elif (data["packet_type"] == PACKET_T.QUERY_VM_DISTRIBUTION) :
            self.__sendStatusData(self.__commandsDBConnector.getHostedImages, self.__packetHandler.createVMDistributionPacket)
        elif (data["packet_type"] == PACKET_T.QUERY_ACTIVE_VM_VNC_DATA) :
            self.__requestVNCConnectionData()
        elif (data["packet_type"] == PACKET_T.DOMAIN_DESTRUCTION) :
            self.__destroyOrRebootDomain(data, False)
        elif (data["packet_type"] == PACKET_T.DOMAIN_REBOOT) :
            self.__destroyOrRebootDomain(data, True)
        elif (data["packet_type"] == PACKET_T.VM_SERVER_CONFIGURATION_CHANGE):
            self.__changeVMServerConfiguration(data)
        elif (data["packet_type"] == PACKET_T.QUERY_REPOSITORY_STATUS):
            self.__sendRepositoryStatusData()
        elif (data["packet_type"] == PACKET_T.DEPLOY_IMAGE or data["packet_type"] == PACKET_T.DELETE_IMAGE_FROM_SERVER):
            self.__deployOrDeleteImage(data)
        elif (data["packet_type"] == PACKET_T.CREATE_IMAGE or data["packet_type"] == PACKET_T.EDIT_IMAGE):
            self.__createOrEditImage(data)
        elif (data["packet_type"] == PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE):
            self.__deleteImageFromInfrastructure(data)
        elif (data["packet_type"] == PACKET_T.AUTO_DEPLOY):
            self.__auto_deploy_image(data)
        elif (data["packet_type"] == PACKET_T.QUERY_VM_SERVERS_RESOURCE_USAGE):
            self.__sendStatusData(self.__commandsDBConnector.getVMServerStatisticsToSend, self.__packetHandler.createVMServerResourceUsagePacket)
        
            
    def __registerVMServer(self, data):
        """
        Processes a virtual machine server registration packet
        Args:
            data: a dictionary containing the incoming packet's data
        Returns:
            Nothing
        """
        try :
            # Comprobar si la IP y el nombre del servidor ya están en uso
            server_id = self.__commandsDBConnector.getVMServerID(data["VMServerIP"])
            if (server_id != None) :
                raise Exception("The IP address " + data["VMServerIP"] + " is assigned to another VM server")
          
            server_id = self.__commandsDBConnector.getVMServerID(data["VMServerName"])
            if (server_id != None) :
                raise Exception("The name " + data["VMServerName"] + " is assigned to another VM server")
            
            # Establecer la conexión
            self.__networkManager.connectTo(data["VMServerIP"], data["VMServerPort"], 
                                                20, self.__vmServerCallback, self.__useSSL, True)            
            while not self.__networkManager.isConnectionReady(data["VMServerIP"], data["VMServerPort"]) :
                sleep(0.1)
                
            # Registrar el nuevo servidor y pedirle su estado
            self.__commandsDBConnector.registerVMServer(data["VMServerName"], data["VMServerIP"], 
                                                    data["VMServerPort"], data["IsEditionServer"])            
            
            # Indicar al endpoint de la web que el comando se ha ejecutado con éxito
            p = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])
        except Exception:                
            p = self.__packetHandler.createErrorPacket(PACKET_T.VM_SERVER_REGISTRATION_ERROR,
                                                          ERROR_DESC_T.CLSRVR_VMSRVR_CONNECTION_ERROR, data["CommandID"])        
        self.__networkManager.sendPacket('', self.__listenningPort, p)
        
    def __bootVMServer(self, data):
        """
        Processes a virtual machine server boot packet
        Args:
            data: a dictionary containing the incoming packet's data
        Returns:
            Nothing
        """
        try :             
            serverNameOrIPAddress = data["ServerNameOrIPAddress"]
            serverId = self.__commandsDBConnector.getVMServerID(serverNameOrIPAddress)
            if (serverId == None) :
                p = self.__packetHandler.createErrorPacket(PACKET_T.VM_SERVER_BOOTUP_ERROR, 
                                                              ERROR_DESC_T.CLSRVR_UNKNOWN_VMSRVR, data["CommandID"])
            else :
                serverData = self.__commandsDBConnector.getVMServerConfiguration(serverId)
                
                if (serverData["ServerStatus"] == SERVER_STATE_T.SHUT_DOWN or 
                    serverData["ServerStatus"] == SERVER_STATE_T.CONNECTION_TIMED_OUT) :                   
                
                    self.__networkManager.connectTo(serverData["ServerIP"], serverData["ServerPort"], 
                                                        20, self.__vmServerCallback, self.__useSSL, True)
                    while not self.__networkManager.isConnectionReady(serverData["ServerIP"], serverData["ServerPort"]) :
                        sleep(0.1)
                        
                    self.__commandsDBConnector.updateVMServerStatus(serverId, SERVER_STATE_T.BOOTING)       
                    
                    imagesToDeploy = self.__commandsDBConnector.getHostedImagesInState(serverId, IMAGE_STATE_T.DEPLOY)
                    for imageID in imagesToDeploy :
                        familyID = self.__commandsDBConnector.getImageVMFamilyID(imageID)
                        familyFeatures = self.__commandsDBConnector.getVMFamilyFeatures(familyID)
                        p = self.__vmServerPacketHandler.createImageDeploymentPacket(self.__repositoryIP, self.__repositoryPort, imageID, 
                                                                                     self.__commandsDBConnector.getImageEditionCommandID(imageID))
                        self.__commandsDBConnector.allocateVMServerResources(data["CommandID"], serverId, 
                                                                 0, familyFeatures["osDiskSize"] + familyFeatures["dataDiskSize"], 
                                                                 0, 0, 1)
                        self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)
                        
                    imagesToDelete = self.__commandsDBConnector.getHostedImagesInState(serverId, IMAGE_STATE_T.DELETE)            
                    for imageID in imagesToDelete :
                        p = self.__vmServerPacketHandler.createDeleteImagePacket(imageID, self.__commandsDBConnector.getImageDeletionCommandID(imageID))
                        self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)
                
                p = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])
        except Exception:
            p = self.__packetHandler.createErrorPacket(PACKET_T.VM_SERVER_BOOTUP_ERROR,
                                                          ERROR_DESC_T.CLSRVR_VMSRVR_CONNECTION_ERROR, data["CommandID"])
        self.__networkManager.sendPacket('', self.__listenningPort, p)       
        
    def __bootVM(self, data):
        """
        Processes a virtual machine server boot packet
        Args:
            data: a dictionary containing the incoming packet's data
        Returns:
            Nothing
        """
        vmID = data["VMID"]
        userID = data["UserID"]
        
        (serverID, errorDescription) = self.__loadBalancer.assignVMServer(vmID, MODE_T.BOOT_DOMAIN)
        if (errorDescription != None) :
            p = self.__packetHandler.createErrorPacket(PACKET_T.VM_BOOT_FAILURE, errorDescription, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)
        else :           
            familyID = self.__commandsDBConnector.getImageVMFamilyID(vmID)
            familyFeatures = self.__commandsDBConnector.getVMFamilyFeatures(familyID)
            self.__commandsDBConnector.allocateVMServerResources(data["CommandID"], serverID, 
                                                         familyFeatures["RAMSize"], 0, familyFeatures["dataDiskSize"], 
                                                         familyFeatures["vCPUs"], 1)
            p = self.__vmServerPacketHandler.createVMBootPacket(vmID, userID, data["CommandID"])
            serverData = self.__commandsDBConnector.getVMServerConfiguration(serverID)
            error = self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)    
            if (error != None) :
                p = self.__packetHandler.createErrorPacket(PACKET_T.VM_BOOT_FAILURE, 
                                                              ERROR_DESC_T.CLSRVR_VMSRVR_CONNECTION_LOST, data["CommandID"])
                self.__networkManager.sendPacket('', self.__listenningPort, p)
                self.__commandsDBConnector.freeVMServerResources(data["CommandID"], True)
                return              
            self.__commandsDBConnector.registerActiveVMLocation(data["CommandID"], serverID)
            self.__commandsDBConnector.registerVMBootCommand(data["CommandID"], data["VMID"])            
            
    def __auto_deploy_image(self, data):       
        """
        Processes an image auto-deployment packet
        Args:
            data: a dictionary containing the incoming packet's data
        Returns:
            Nothing
        """
        if (data["Instances"] == 0 or data["Instances"] < -1) :
            p = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)        
            return  
        
        familyID = self.__commandsDBConnector.getImageVMFamilyID(data["ImageID"])
        if (familyID == None) :
            p = self.__packetHandler.createErrorPacket(PACKET_T.AUTO_DEPLOY_ERROR, ERROR_DESC_T.CLSRVR_UNKNOWN_IMAGE, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)        
            return  
        
        familyFeatures = self.__commandsDBConnector.getVMFamilyFeatures(familyID)
         
        if (data["Instances"] == -1) :
            if (not self.__commandsDBConnector.isBeingDeleted(data["ImageID"])) :                 
                self.__commandsDBConnector.changeImageCopiesState(data["ImageID"], IMAGE_STATE_T.DEPLOY)
                
                serverIDs = self.__commandsDBConnector.getHosts(data["ImageID"], IMAGE_STATE_T.DEPLOY)
                if (serverIDs != []) :
                    self.__commandsDBConnector.addImageEditionCommand(data["CommandID"], data["ImageID"]) 
                                       
                    p = self.__vmServerPacketHandler.createImageDeploymentPacket(self.__repositoryIP, self.__repositoryPort, data["ImageID"], data["CommandID"])
                    for serverID in serverIDs :
                        self.__commandsDBConnector.allocateVMServerResources(data["CommandID"], serverID, 
                                                         0, familyFeatures["osDiskSize"] + familyFeatures["dataDiskSize"], 
                                                         0, 0, 1)
                        connectionData = self.__commandsDBConnector.getVMServerConfiguration(serverID)
                        self.__networkManager.sendPacket(connectionData["ServerIP"], connectionData["ServerPort"], p)   
                else :
                    if (not self.__commandsDBConnector.isThereSomeImageCopyInState(data["ImageID"], IMAGE_STATE_T.EDITED)) :
                        p = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])
                        self.__networkManager.sendPacket('', self.__listenningPort, p)
            else :
                p = self.__packetHandler.createErrorPacket(PACKET_T.AUTO_DEPLOY_ERROR, ERROR_DESC_T.CLSRVR_NOT_EDITED_IMAGE, 
                                                                     data["CommandID"])
                self.__networkManager.sendPacket('', self.__listenningPort, p)  
        elif (data["Instances"] > 0) :
            if (self.__commandsDBConnector.isAffectedByAutoDeploymentCommand(data["ImageID"])) :
                p = self.__packetHandler.createErrorPacket(PACKET_T.AUTO_DEPLOY_ERROR, ERROR_DESC_T.CLSRVR_AUTODEPLOYED, 
                                                                     data["CommandID"])
                self.__networkManager.sendPacket('', self.__listenningPort, p)  
                return
            output = self.__loadBalancer.assignVMServer(data["ImageID"], MODE_T.DEPLOY_IMAGE)
            if (output[1] != None) :
                p = self.__packetHandler.createErrorPacket(PACKET_T.AUTO_DEPLOY_ERROR, output[1], data["CommandID"])
                self.__networkManager.sendPacket('', self.__listenningPort, p)  
            else :
                if (output[2] < data["Instances"]) :
                    p = self.__packetHandler.createErrorPacket(PACKET_T.AUTO_DEPLOY_ERROR, 
                                                                  ERROR_DESC_T.CLSRVR_AUTOD_TOO_MANY_INSTANCES, data["CommandID"])
                    self.__networkManager.sendPacket('', self.__listenningPort, p)  
                else :
                    
                    servers = []
                    deployed_copies = 0
                    i = 0
                    while (deployed_copies < data["Instances"]) :
                        servers.append(output[i][0][0])                             
                        deployed_copies += output[i][0][1]
                        i += 1
                                                
                    self.__commandsDBConnector.addAutoDeploymentCommand(data["CommandID"], data["ImageID"], len(servers))
                    
                    p = self.__vmServerPacketHandler.createImageDeploymentPacket(self.__repositoryIP, self.__repositoryPort, data["ImageID"], data["CommandID"])                    
                    for serverID in servers:                        
                        self.__commandsDBConnector.allocateVMServerResources(data["CommandID"], serverID, 
                                                         0, familyFeatures["osDiskSize"] + familyFeatures["dataDiskSize"], 
                                                         0, 0, 1)
                        connectionData = self.__commandsDBConnector.getVMServerConfiguration(serverID)            
                        self.__networkManager.sendPacket(connectionData["ServerIP"], connectionData["ServerPort"], p)     

    def __deleteImageFromInfrastructure(self, data):
        """
        Processes a complete image deletion packet
        Args:
            data: a dictionary containing the incoming packet's data
        Returns:
            Nothing
        """
        errorDescription = None
        if (self.__commandsDBConnector.isBeingEdited(data["ImageID"])) :
            errorDescription = ERROR_DESC_T.CLSRVR_LOCKED_IMAGE
        elif (self.__commandsDBConnector.isBeingDeleted(data["ImageID"])) :
            errorDescription = ERROR_DESC_T.CLSRVR_DELETED_IMAGE
        elif (self.__commandsDBConnector.getImageVMFamilyID(data["ImageID"]) == None) :
            errorDescription = ERROR_DESC_T.CLSRVR_UNKNOWN_IMAGE
        if (errorDescription != None) :
            p = self.__packetHandler.createErrorPacket(PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR, errorDescription, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)
        else :
            
            p = self.__vmServerPacketHandler.createDeleteImagePacket(data["ImageID"], data["CommandID"])
            
            for serverID in self.__commandsDBConnector.getHosts(data["ImageID"], IMAGE_STATE_T.DELETE) :
                serverData = self.__commandsDBConnector.getVMServerConfiguration(serverID)
                self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)
            
            self.__commandsDBConnector.changeImageCopiesState(data["ImageID"], IMAGE_STATE_T.DELETE)
            self.__commandsDBConnector.deleteImageVMFamilyID(data["ImageID"])
            self.__commandsDBConnector.addImageDeletionCommand(data["CommandID"], data["ImageID"])
            p = self.__imageRepositoryPacketHandler.createDeleteRequestPacket(data["ImageID"])
            self.__networkManager.sendPacket(self.__repositoryIP, self.__repositoryPort, p)                
            
    def __createOrEditImage(self, data):    
        """
        Processes an image creation or an image edition incoming packet
        Args:
            data: a dictionary containing the incoming packet's data
        Returns:
            Nothing
        """                  
        errorDescription = None
        
        if (self.__commandsDBConnector.isBeingEdited(data["ImageID"])) :
            errorDescription = ERROR_DESC_T.CLSRVR_LOCKED_IMAGE
        elif (self.__commandsDBConnector.isBeingDeleted(data["ImageID"])) :    
            errorDescription = ERROR_DESC_T.CLSRVR_DELETED_IMAGE
        elif (self.__commandsDBConnector.getImageVMFamilyID(data["ImageID"]) == None) :
            errorDescription = ERROR_DESC_T.CLSRVR_UNKNOWN_IMAGE
        elif (data["packet_type"] == PACKET_T.CREATE_IMAGE):
            repositoryStatus = self.__commandsDBConnector.getImageRepositoryStatus(self.__repositoryIP, self.__repositoryPort)
            if (repositoryStatus == None) :
                errorDescription = ERROR_DESC_T.CLSRVR_IR_CONNECTION_ERROR
            else :
                imageFeatures = self.__commandsDBConnector.getVMFamilyFeatures(self.__commandsDBConnector.getImageVMFamilyID(data["ImageID"]))
                required_disk_space = imageFeatures["osDiskSize"] + imageFeatures["dataDiskSize"]
                required_disk_space = self.__averageCompressionRatio * required_disk_space
                remaining_disk_space = repositoryStatus["FreeDiskSpace"] - required_disk_space
                if (remaining_disk_space < 0) :
                    errorDescription = ERROR_DESC_T.CLSRVR_IR_NO_DISK_SPACE
        
        if (errorDescription != None) :        
            if (data["packet_type"] == PACKET_T.CREATE_IMAGE) :
                packet_type = PACKET_T.IMAGE_CREATION_ERROR
            else :
                packet_type = PACKET_T.IMAGE_EDITION_ERROR  
            p = self.__packetHandler.createErrorPacket(packet_type, errorDescription, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)
            return           
        
        (serverID, errorDescription) = self.__loadBalancer.assignVMServer(data["ImageID"], MODE_T.CREATE_OR_EDIT_IMAGE)
        if (errorDescription != None) :
            if (data["packet_type"] == PACKET_T.CREATE_IMAGE) :
                packet_type = PACKET_T.IMAGE_CREATION_ERROR
            else :
                packet_type = PACKET_T.IMAGE_EDITION_ERROR
            p = self.__packetHandler.createErrorPacket(packet_type, errorDescription, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)
            return
        
        if (data["packet_type"] == PACKET_T.CREATE_IMAGE) :
            self.__commandsDBConnector.registerNewImageVMFamily(data["CommandID"], self.__commandsDBConnector.getImageVMFamilyID(data["ImageID"]))
            modify = False
        else :
            self.__commandsDBConnector.addImageEditionCommand(data["CommandID"], data["ImageID"])
            modify = True
            
        familyID = self.__commandsDBConnector.getImageVMFamilyID(data["ImageID"])
        familyFeatures = self.__commandsDBConnector.getVMFamilyFeatures(familyID)
        zipFileAllocatedSpace = self.__averageCompressionRatio * (familyFeatures["osDiskSize"] + familyFeatures["dataDiskSize"])
        self.__commandsDBConnector.allocateVMServerResources(data["CommandID"], serverID, 
                                                         familyFeatures["RAMSize"], familyFeatures["osDiskSize"] + familyFeatures["dataDiskSize"], 
                                                         zipFileAllocatedSpace, 
                                                         familyFeatures["vCPUs"], 1)
        self.__commandsDBConnector.allocateImageRepositoryResources(self.__repositoryIP, self.__repositoryPort, data["CommandID"], 
            zipFileAllocatedSpace)
        
        connectionData = self.__commandsDBConnector.getVMServerConfiguration(serverID)
        p = self.__vmServerPacketHandler.createImageEditionPacket(self.__repositoryIP, self.__repositoryPort, data["ImageID"], modify, data["CommandID"], 
                                                                  data["OwnerID"])
        self.__networkManager.sendPacket(connectionData["ServerIP"], connectionData["ServerPort"], p)
        self.__commandsDBConnector.registerActiveVMLocation(data["CommandID"], serverID)        
            
    def __deployOrDeleteImage(self, data):
        """
        Processes an image deployment or an image deletion incoming packet
        Args:
            data: a dictionary containing the incoming packet's data
        Returns:
            Nothing
        """
        serverNameOrIPAddress = data["ServerNameOrIPAddress"]
        serverID = self.__commandsDBConnector.getVMServerID(serverNameOrIPAddress)        
        serverData = self.__commandsDBConnector.getVMServerConfiguration(serverID)
        errorDescription = None        
            
        if (self.__commandsDBConnector.isBeingEdited(data["ImageID"])) :
            errorDescription = ERROR_DESC_T.CLSRVR_LOCKED_IMAGE
        elif (self.__commandsDBConnector.isBeingDeleted(data["ImageID"])):
            errorDescription = ERROR_DESC_T.CLSRVR_DELETED_IMAGE
        elif (self.__commandsDBConnector.getImageVMFamilyID(data["ImageID"]) == None) :
            errorDescription = ERROR_DESC_T.CLSRVR_UNKNOWN_IMAGE
        elif (serverID == None) :
            errorDescription =  ERROR_DESC_T.CLSRVR_UNKNOWN_VMSRVR
        elif (serverData["ServerStatus"] != SERVER_STATE_T.READY):
            errorDescription = ERROR_DESC_T.CLSRVR_VMSRVR_NOT_READY
        elif (data["packet_type"] == PACKET_T.DEPLOY_IMAGE and self.__commandsDBConnector.hostsImage(serverID, data["ImageID"]))\
            or (data["packet_type"] == PACKET_T.DELETE_IMAGE_FROM_SERVER and not self.__commandsDBConnector.hostsImage(serverID, data["ImageID"])):
            
            if (data["packet_type"] == PACKET_T.DEPLOY_IMAGE):
                errorDescription = ERROR_DESC_T.CLSRVR_IMAGE_HOSTED_ON_VMSRVR
            else :
                errorDescription = ERROR_DESC_T.CLSRVR_IMAGE_NOT_HOSTED_ON_VMSRVR
        elif (data["packet_type"] == PACKET_T.DEPLOY_IMAGE):
            free_disk_space = self.__commandsDBConnector.getVMServerStatistics(serverID)["FreeStorageSpace"]
            familyID = self.__commandsDBConnector.getImageVMFamilyID(data["ImageID"])
            familyFeatures = self.__commandsDBConnector.getVMFamilyFeatures(familyID)
            required_disk_space = familyFeatures["osDiskSize"] + familyFeatures["dataDiskSize"]
            if (free_disk_space < required_disk_space) :
                errorDescription = ERROR_DESC_T.CLSRVR_VMSRVR_NO_DISK_SPACE
            
        if (errorDescription != None) :       
            if (data["packet_type"] == PACKET_T.DEPLOY_IMAGE):
                error_type = PACKET_T.IMAGE_DEPLOYMENT_ERROR
            else:
                error_type = PACKET_T.DELETE_IMAGE_FROM_SERVER_ERROR 
            p = self.__packetHandler.createErrorPacket(error_type, errorDescription, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)
            return
           
        if (data["packet_type"] == PACKET_T.DEPLOY_IMAGE) :
            familyID = self.__commandsDBConnector.getImageVMFamilyID(data["ImageID"])
            familyFeatures = self.__commandsDBConnector.getVMFamilyFeatures(familyID)
            self.__commandsDBConnector.allocateVMServerResources(data["CommandID"], serverID, 0, familyFeatures["osDiskSize"] + familyFeatures["dataDiskSize"], 
                                                         0, 0, 0)
            p = self.__vmServerPacketHandler.createImageDeploymentPacket(self.__repositoryIP, self.__repositoryPort, data["ImageID"], data["CommandID"])
        else:
            p = self.__vmServerPacketHandler.createDeleteImagePacket(data["ImageID"], data["CommandID"])
        self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)        
            
    def __sendRepositoryStatusData(self):
        """
        Processes an image repository status request packet
        Args:
            data: a dictionary containing the incoming packet's data
        Returns:
            Nothing
        """
        repositoryStatus = self.__commandsDBConnector.getImageRepositoryStatus(self.__repositoryIP, self.__repositoryPort)
        p = self.__packetHandler.createRepositoryStatusPacket(repositoryStatus["FreeDiskSpace"], 
                                                                 repositoryStatus["AvailableDiskSpace"], 
                                                                 repositoryStatus["ConnectionStatus"])
        self.__networkManager.sendPacket('', self.__listenningPort, p)
        
    def __unregisterOrShutdownVMServer(self, data):
        """
        Unregisters or shuts down a virtual machine server
        Args:
            data: a dictionary containing the incoming packet's data
        Returns:
            Nothing
        """
        key = data["ServerNameOrIPAddress"] 
        haltServer = data["Halt"]
        unregister = data["Unregister"]
        
        if data.has_key("CommandID") :
            useCommandID = True 
            commandID = data["CommandID"]
        else :
            useCommandID = False
            commandID = ""
            
        serverID = self.__commandsDBConnector.getVMServerID(key)
        if (serverID == None) :            
            if (unregister) :
                packet_type = PACKET_T.VM_SERVER_UNREGISTRATION_ERROR
            else :
                packet_type = PACKET_T.VM_SERVER_SHUTDOWN_ERROR
            p = self.__packetHandler.createErrorPacket(packet_type, key, ERROR_DESC_T.CLSRVR_UNKNOWN_VMSRVR, commandID)
            self.__networkManager.sendPacket('', self.__listenningPort, p)  
            return
        
        serverData = self.__commandsDBConnector.getVMServerConfiguration(serverID)            
        status = serverData["ServerStatus"]    
        if (status == SERVER_STATE_T.READY or status == SERVER_STATE_T.BOOTING) :  
            try :
                connectionReady = self.__networkManager.isConnectionReady(serverData["ServerIP"], serverData["ServerPort"])
            except Exception:
                connectionReady = False                 
            if (not connectionReady) :   
                if (unregister) :
                    packet_type = PACKET_T.VM_SERVER_UNREGISTRATION_ERROR
                else :
                    packet_type = PACKET_T.VM_SERVER_SHUTDOWN_ERROR
                p = self.__packetHandler.createErrorPacket(packet_type, ERROR_DESC_T.CLSRVR_VMSRVR_CONNECTION_ERROR, commandID)
                self.__networkManager.sendPacket('', self.__listenningPort, p)  
                return
            
            self.__commandsDBConnector.deleteHostedVMs(serverID)
            if not haltServer :
                p = self.__vmServerPacketHandler.createVMServerShutdownPacket()
            else :
                p = self.__vmServerPacketHandler.createVMServerHaltPacket()
                self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)
                     
            self.__networkManager.closeConnection(serverData["ServerIP"], serverData["ServerPort"])       
            
        if (unregister) :
            self.__commandsDBConnector.deleteVMServer(key)
        else:
            self.__commandsDBConnector.updateVMServerStatus(serverID, SERVER_STATE_T.SHUT_DOWN)
            
        if (useCommandID) :
            p = self.__packetHandler.createCommandExecutedPacket(commandID)
            self.__networkManager.sendPacket('', self.__listenningPort, p)
        
    def __sendStatusData(self, queryMethod, packetCreationMethod):
        """
        Processes a status request packet
        Args:
            data: a dictionary containing the incoming packet's data
        Returns:
            Nothing
        """              
        segmentSize = 100 
        outgoingData = []
        serverIDs = self.__commandsDBConnector.getVMServerIDs()
        if (len(serverIDs) == 0) :
            segmentCounter = 0
            segmentNumber = 0
            sendLastSegment = True
        else :
            segmentCounter = 1        
            segmentNumber = (len(serverIDs) / segmentSize)
            if (len(serverIDs) % segmentSize != 0) :
                segmentNumber += 1
                sendLastSegment = True
            else :
                sendLastSegment = False  
                
        for serverID in serverIDs :
            row = queryMethod(serverID)
            if (row == None):
                break
            if (isinstance(row, dict)) :
                outgoingData.append(row)
            else :
                outgoingData += row
                
            if (len(outgoingData) >= segmentSize) :
                packet = packetCreationMethod(segmentCounter, segmentNumber, outgoingData)
                self.__networkManager.sendPacket('', self.__listenningPort, packet)
                outgoingData = []
                segmentCounter += 1
                
        if (sendLastSegment) :
            packet = packetCreationMethod(segmentCounter, segmentNumber, outgoingData)
            self.__networkManager.sendPacket('', self.__listenningPort, packet) 
            
    def __doImmediateShutdown(self, data):
        """
        Processes a halt packet
        Args:
            data: a dictionary containing the incoming packet's data
        Returns:
            Nothing
        """ 
        p = self.__imageRepositoryPacketHandler.createHaltPacket()
        self.__networkManager.sendPacket(self.__repositoryIP, self.__repositoryPort, p)
        self.__networkManager.closeConnection(self.__repositoryIP, self.__repositoryPort)
        vmServersConnectionData = self.__commandsDBConnector.getActiveVMServersConnectionData()
        if (vmServersConnectionData != None) :
            args = dict()
            args["Halt"] = data["HaltVMServers"]
            args["Unregister"] = False            
            for connectionData in vmServersConnectionData :
                args["ServerNameOrIPAddress"] = connectionData["ServerIP"]
                self.__unregisterOrShutdownVMServer(args)  
        self.__finished = True       
        
    def __requestVNCConnectionData(self):
        """
        Processes a VNC connection data request packet
        Args:
            data: a dictionary containing the incoming packet's data
        Returns:
            Nothing
        """
        p = self.__vmServerPacketHandler.createVMServerDataRequestPacket(VMSRVR_PACKET_T.QUERY_ACTIVE_VM_DATA)
        
        connectionData = self.__commandsDBConnector.getActiveVMServersConnectionData()
        for cd in connectionData :            
            errorMessage = self.__networkManager.sendPacket(cd["ServerIP"], cd["ServerPort"], p)
            NetworkManager.printConnectionWarningIfNecessary(cd["ServerIP"], cd["ServerPort"], "VNC connection data request", errorMessage)   
            
    def __destroyOrRebootDomain(self, data, reboot):
        """
        Processes a domain destruction or a domain reboot packet
        Args:
            data: a dictionary containing the incoming packet's data
        Returns:
            Nothing
        """
        serverID = self.__commandsDBConnector.getActiveVMHostID(data["DomainID"])
        if (serverID == None) :
            if (reboot) :
                packet_type = PACKET_T.DOMAIN_REBOOT_ERROR
            else:
                packet_type = PACKET_T.DOMAIN_DESTRUCTION_ERROR
            packet = self.__packetHandler.createErrorPacket(packet_type, 
                                                                      ERROR_DESC_T.CLSRVR_DOMAIN_NOT_REGISTERED, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, packet)
            return       
        
        connectionData = self.__commandsDBConnector.getVMServerConfiguration(serverID)
        if (reboot) :
            packet = self.__vmServerPacketHandler.createVMRebootPacket(data["DomainID"])
        else :
            packet = self.__vmServerPacketHandler.createVMShutdownPacket(data["DomainID"])
        errorMessage = self.__networkManager.sendPacket(connectionData["ServerIP"], connectionData["ServerPort"], packet)
        if (errorMessage != None) :
            if (reboot) :
                packet_type = PACKET_T.DOMAIN_REBOOT_ERROR
            else:
                packet_type = PACKET_T.DOMAIN_DESTRUCTION_ERROR
            packet = self.__packetHandler.createErrorPacket(packet_type, ERROR_DESC_T.CLSRVR_VMSRVR_CONNECTION_LOST, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, packet)
        else :
            if (not reboot) :
                self.__commandsDBConnector.deleteActiveVMLocation(data["CommandID"])         
            packet = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, packet)
            
    def __changeVMServerConfiguration(self, data):
        """
        Processes a virtual machine server configuration change packet
        Args:
            data: a dictionary containing the incoming packet's data
        Returns:
            Nothing
        """
        serverID = self.__commandsDBConnector.getVMServerID(data["ServerNameOrIPAddress"])
        
        if (serverID == None) :
            packet = self.__packetHandler.createErrorPacket(PACKET_T.VM_SERVER_CONFIGURATION_CHANGE_ERROR,
                ERROR_DESC_T.CLSRVR_UNKNOWN_VMSRVR, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, packet)
            return
        
        status = self.__commandsDBConnector.getVMServerConfiguration(serverID)["ServerStatus"]
        
        if (status == SERVER_STATE_T.BOOTING or status == SERVER_STATE_T.READY) :
            packet = self.__packetHandler.createErrorPacket(PACKET_T.VM_SERVER_CONFIGURATION_CHANGE_ERROR,
                ERROR_DESC_T.CLSRVR_ACTIVE_VMSRVR, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, packet)
            return
            
        try :
            self.__commandsDBConnector.setServerBasicData(serverID, data["NewVMServerName"], SERVER_STATE_T.SHUT_DOWN, 
                                                  data["NewVMServerIPAddress"], data["NewVMServerPort"], data["NewImageEditionBehavior"])
            packet = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])
        
        except Exception :
            packet = self.__packetHandler.createErrorPacket(PACKET_T.VM_SERVER_CONFIGURATION_CHANGE_ERROR,
               ERROR_DESC_T.CLSRVR_VMSRVR_IDS_IN_USE, data["CommandID"])
            
        self.__networkManager.sendPacket('', self.__listenningPort, packet)    
        
    def hasFinished(self):
        """
        Indicates if a halt packet was received or not
        Args:
            None
        Returns:
            True if a halt packet was received, and False if it wasn't
        """
        return self.__finished