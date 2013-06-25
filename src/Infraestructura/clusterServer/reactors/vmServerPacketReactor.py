# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: vmServerPacketReactor.py    
    Version: 5.0
    Description: virtual machine server packet reactor definition
    
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

from virtualMachineServer.packetHandling.packet_t import VM_SERVER_PACKET_T as VMSRVR_PACKET_T
from clusterServer.packetHandling.packet_t import CLUSTER_SERVER_PACKET_T as ENDPOINT_PACKET_T
from clusterServer.database.server_state_t import SERVER_STATE_T
from clusterServer.database.image_state_t import IMAGE_STATE_T
from time import sleep
from errors.codes import ERROR_DESC_T

class VMServerPacketReactor(object):
    """
    These objects process the packets sent from the virtual machine servers
    """
    def __init__(self, dbConnector, networkManager, listenningPort, vmServerPacketHandler, clusterServerPacketHandler):
        """
        Initializes the reactor's state
        Args:
            dbConnector: a cluster server database connector
            networkManager: the network manager to use
            listenningPort: the control connection's listenning port            
            vmServerPacketHandler: the virtual machine server packet handler            
            clusterServerPacketHandler: the cluster server packet handler
        """
        self.__dbConnector = dbConnector        
        self.__networkManager = networkManager
        self.__listenningPort = listenningPort
        self.__vmServerPacketHandler = vmServerPacketHandler
        self.__packetHandler = clusterServerPacketHandler
    
    def processVMServerIncomingPacket(self, packet):
        """
        Processes a packet sent from a virtual machine server
        Args:
            packet: the packet to process
        Returns:
            Nothing
        """        
        data = self.__vmServerPacketHandler.readPacket(packet)
        if (data["packet_type"] == VMSRVR_PACKET_T.SERVER_STATUS) :
            self.__updateVMServerStatus(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.DOMAIN_CONNECTION_DATA) :
            self.__sendVMConnectionData(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.ACTIVE_VM_DATA) :
            self.__sendDomainsVNCConnectionData(packet)
        elif (data["packet_type"] == VMSRVR_PACKET_T.ACTIVE_DOMAIN_UIDS) :
            self.__processActiveDomainUIDs(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.IMAGE_DEPLOYMENT_ERROR or data["packet_type"] == VMSRVR_PACKET_T.IMAGE_DELETION_ERROR):
            self.__processImageDeploymentErrorPacket(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.IMAGE_DEPLOYED or data["packet_type"] == VMSRVR_PACKET_T.IMAGE_DELETED):
            self.__processImageDeploymentPacket(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.IMAGE_EDITED):
            self.__processImageEditedPacket(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.IMAGE_EDITION_ERROR):
            self.__processImageEditionError(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.INTERNAL_ERROR) :
            self.__processVMServerInternalError(data)
            
    def __updateVMServerStatus(self, data):
        """
        Processes a virtual machine server status packet
        Args:
            data: a dictionary containing the received packet's data
        Returns:
            Nothing
        """        
        serverID = None
        while (serverID == None) :
            serverID = self.__dbConnector.getVMServerID(data["VMServerIP"])
            if (serverID == None) :
                sleep(0.1)
                
        self.__dbConnector.updateVMServerStatus(serverID, SERVER_STATE_T.READY)
        self.__dbConnector.setVMServerStatistics(serverID, data["ActiveDomains"], data["RAMInUse"], data["RAMSize"], 
                                                 data["FreeStorageSpace"], data["AvailableStorageSpace"], data["FreeTemporarySpace"],
                                                 data["AvailableTemporarySpace"], data["ActiveVCPUs"], data["PhysicalCPUs"])
            
    def __processVMServerInternalError(self, data):
        """
        Processes a virtual machine server internal error packet
        Args:
            data: a dictionary containing the received packet's data
        Returns:
            Nothing

        """
        self.__dbConnector.freeVMServerResources(data["CommandID"], True)
        p = self.__packetHandler.createErrorPacket(ENDPOINT_PACKET_T.VM_SERVER_INTERNAL_ERROR, ERROR_DESC_T.VMSRVR_INTERNAL_ERROR, data["CommandID"])
        self.__networkManager.sendPacket('', self.__listenningPort, p)
        
    def __processImageEditedPacket(self, data):
        """
        Processes an image edited packet
        Args:
            data: a dictionary containing the received packet's data
        Returns:
            Nothing
        """
        self.__dbConnector.deleteActiveVMLocation(data["CommandID"])
        if (not self.__dbConnector.isImageEditionCommand(data["CommandID"])) :            
            familyID = self.__dbConnector.getNewImageVMFamily(data["CommandID"])
            self.__dbConnector.deleteNewImageVMFamily(data["CommandID"])
            self.__dbConnector.registerFamilyID(data["ImageID"], familyID)           
                 
            p = self.__packetHandler.createImageEditedPacket(data["CommandID"], data["ImageID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)
        else :
            self.__dbConnector.removeImageEditionCommand(data["CommandID"])
            self.__dbConnector.changeImageStatus(data["ImageID"], IMAGE_STATE_T.EDITED)  
            p = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)   
        
        self.__dbConnector.freeVMServerResources(data["CommandID"], False)        
        self.__dbConnector.freeImageRepositoryResources(data["CommandID"], False) 
    
    def __processImageEditionError(self, data):
        """
        Processes an image edition error packet
        Args:
            data: a dictionary containing the received packet's data
        Returns:
            Nothing
        """
        if (not self.__dbConnector.isImageEditionCommand(data["CommandID"])) :        
            self.__dbConnector.deleteNewImageVMFamily(data["CommandID"])
            packet_type = ENDPOINT_PACKET_T.IMAGE_CREATION_ERROR
        else :
            self.__dbConnector.removeImageEditionCommand(data["CommandID"])
            packet_type = ENDPOINT_PACKET_T.IMAGE_EDITION_ERROR        
            
        p = self.__packetHandler.createErrorPacket(packet_type, data["ErrorDescription"], data["CommandID"])
        self.__networkManager.sendPacket('', self.__listenningPort, p)
        
        self.__dbConnector.freeVMServerResources(data["CommandID"], True)
        self.__dbConnector.freeImageRepositoryResources(data["CommandID"], True)
            
    def __processImageDeploymentErrorPacket(self, data):
        """
        Processes an image deployment error packet
        Args:
            data: a dictionary containing the received packet's data
        Returns:
            Nothing
        """
        if (self.__dbConnector.isImageEditionCommand(data["CommandID"])) :
            packet_type = ENDPOINT_PACKET_T.IMAGE_EDITION_ERROR
            self.__dbConnector.removeImageEditionCommand(data["CommandID"])
            
        elif (self.__dbConnector.isAutoDeploymentCommand(data["CommandID"])) :
            (generateOutput, _unused) = self.__dbConnector.handleAutoDeploymentCommandOutput(data["CommandID"], True)
            if (generateOutput) :              
                p = self.__packetHandler.createErrorPacket(ENDPOINT_PACKET_T.AUTO_DEPLOY_ERROR, ERROR_DESC_T.CLSRVR_AUTOD_ERROR, data["CommandID"])
                self.__networkManager.sendPacket('', self.__listenningPort, p)
                
        elif (data["packet_type"] == VMSRVR_PACKET_T.IMAGE_DEPLOYMENT_ERROR) :
            packet_type = ENDPOINT_PACKET_T.IMAGE_DEPLOYMENT_ERROR
        else :
            packet_type = ENDPOINT_PACKET_T.DELETE_IMAGE_FROM_SERVER_ERROR
            
        p = self.__packetHandler.createErrorPacket(packet_type, data["ErrorDescription"], data["CommandID"])
        self.__networkManager.sendPacket('', self.__listenningPort, p)
        
        self.__dbConnector.freeVMServerResources(data["CommandID"], True)
        
    def __processImageDeploymentPacket(self, data):
        """
        Processes an image deployment packet
        Args:
            data: a dictionary containing the received packet's data
        Returns:
            Nothing
        """
        self.__dbConnector.freeVMServerResources(data["CommandID"], False)
        
        serverID = self.__dbConnector.getVMServerID(data["SenderIP"])
        if (self.__dbConnector.isImageEditionCommand(data["CommandID"])) :                      
            self.__dbConnector.changeImageCopyStatus(data["ImageID"], serverID, IMAGE_STATE_T.READY)
            
            if (not self.__dbConnector.isThereSomeImageCopyInState(data["ImageID"], IMAGE_STATE_T.DEPLOY)) :
                p = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])
                self.__networkManager.sendPacket('', self.__listenningPort, p)
                self.__dbConnector.removeImageEditionCommand(data["CommandID"])
                
        elif (self.__dbConnector.isImageDeletionCommand(data["CommandID"])) :
            
            self.__dbConnector.deleteImageFromServer(serverID, data["ImageID"])
            
            if (not self.__dbConnector.isThereSomeImageCopyInState(data["ImageID"], IMAGE_STATE_T.DELETE)) :
                p = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])
                self.__networkManager.sendPacket('', self.__listenningPort, p)
                self.__dbConnector.removeImageDeletionCommand(data["CommandID"])
                
        elif (self.__dbConnector.isAutoDeploymentCommand(data["CommandID"])) :
            (generateOutput, error) = self.__dbConnector.handleAutoDeploymentCommandOutput(data["CommandID"], False)
            
            if (not error) :
                self.__dbConnector.assignImageToServer(serverID, data["ImageID"])
            if (generateOutput) :
                if (error) :
                    p = self.__packetHandler.createErrorPacket(ENDPOINT_PACKET_T.AUTO_DEPLOY_ERROR, ERROR_DESC_T.CLSRVR_AUTOD_ERROR, data["CommandID"])
                else :
                    p = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])                
                self.__networkManager.sendPacket('', self.__listenningPort, p)
                
        else :
            if (data["packet_type"] == VMSRVR_PACKET_T.IMAGE_DEPLOYED) :
                self.__dbConnector.assignImageToServer(serverID, data["ImageID"])                
            else :
                self.__dbConnector.deleteImageFromServer(serverID, data["ImageID"])
            p = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)
        
    def __sendVMConnectionData(self, data):
        """
        Processes a virtual machine connection data packet
        Args:
            data: a dictionary containing the received packet's data
        Returns:
            Nothing
        """
        self.__dbConnector.removeVMBootCommand(data["CommandID"])
        
        p = self.__packetHandler.createVMConnectionDataPacket(data["VNCServerIP"], 
                                                                 data["VNCServerPort"], data["VNCServerPassword"], data["CommandID"])
        self.__networkManager.sendPacket('', self.__listenningPort, p)      
                
        self.__dbConnector.freeVMServerResources(data["CommandID"], False)            
        
    def __processActiveDomainUIDs(self, data):
        """
        Processes an active domains IDs packet
        Args:
            data: a dictionary containing the received packet's data
        Returns:
            Nothing
        """
        vmServerID = self.__dbConnector.getVMServerID(data["VMServerIP"])
        self.__dbConnector.registerHostedVMs(vmServerID, data["Domain_UIDs"])
        
    def __sendDomainsVNCConnectionData(self, packet):
        """
        Redirects an active virtual machines VNC connection data to the cluster endpoint
        Args:
            data: a dictionary containing the received packet's data
        Returns:
            Nothing
        """
        p = self.__packetHandler.createActiveVMsVNCDataPacket(packet)
        self.__networkManager.sendPacket('', self.__listenningPort, p)