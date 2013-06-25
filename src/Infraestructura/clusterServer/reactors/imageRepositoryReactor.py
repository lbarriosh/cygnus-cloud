# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: imageRepositoryPacketReactor.py    
    Version: 5.0
    Description: image repository packet reactor definition
    
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

from imageRepository.packetHandling.packet_t import PACKET_T
from clusterServer.packetHandling.packet_t import CLUSTER_SERVER_PACKET_T
from clusterServer.database.image_state_t import IMAGE_STATE_T

class ImageRepositoryPacketReactor(object):
    """
    These objects process the packets sent from the image repository
    """
    
    def __init__(self, dbConnector, networkManager, listenningPort, 
                 repositoryIP, repositoryPort, clusterServerPacketHandler, vmServerPacketHandler, imageRepositoryPacketHandler):
        """
        Initializes the reactor's state
        Args:
            dbConnector: a cluster server database connector
            networkManager: the network manager to use
            listenningPort: the control connection's listenning port
            repositoryIP: the image repository's IP address
            repositoryPort: the image repository's port            
            clusterServerPacketHandler: the cluster server packet handler
            vmServerPacketHandler: the virtual machine server packet handler
            imageRepositoryPacketHandler: the image repository packet handler
        """
        self.__dbConnector = dbConnector
        self.__networkManager = networkManager
        self.__listenningPort = listenningPort
        self.__repositoryIP = repositoryIP
        self.__repositoryPort = repositoryPort
        self.__packetHandler = clusterServerPacketHandler
        self.__vmServerPacketHandler = vmServerPacketHandler        
        self.__imageRepositoryPacketHandler = imageRepositoryPacketHandler
    
    def processImageRepositoryIncomingPacket(self, packet):
        """
        Processes a packet sent from the image repository
        Args:
            p: the packet to process
        Returns:
            Nothing
        """
        data = self.__imageRepositoryPacketHandler.readPacket(packet)
        if data['packet_type'] == PACKET_T.STATUS_DATA:
            self.__dbConnector.updateImageRepositoryStatus(self.__repositoryIP, self.__repositoryPort, data["FreeDiskSpace"], data["TotalDiskSpace"])
        elif data['packet_type'] == PACKET_T.DELETE_REQUEST_RECVD :
            commandID = self.__dbConnector.getImageDeletionCommandID(data['imageID'])
            if not self.__dbConnector.isThereSomeImageCopyInState(data["imageID"], IMAGE_STATE_T.DELETE) :
                self.__dbConnector.removeImageDeletionCommand(commandID)
                p = self.__packetHandler.createCommandExecutedPacket(commandID)
                self.__networkManager.sendPacket('', self.__listenningPort, p)
            else :
                self.__sendDeleteRequets(data['imageID'], commandID)
        elif data['packet_type'] == PACKET_T.DELETE_REQUEST_ERROR:   
            commandID = self.__dbConnector.getImageDeletionCommandID(data['imageID'])         
            p = self.__packetHandler.createErrorPacket(CLUSTER_SERVER_PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR, data['errorDescription'], commandID)
            self.__networkManager.sendPacket('', self.__listenningPort, p)            
            
    def __sendDeleteRequets(self, imageID, commandID):
        """
        Sends the image delete request to the virtual machine servers
        Args:
            imageID: the affected image's ID
            commandID: a commandID
        Returns:
            Nothing
        """
        p = self.__vmServerPacketHandler.createDeleteImagePacket(imageID, commandID)
        serverIDs = self.__dbConnector.getHosts(imageID, IMAGE_STATE_T.DELETE)
        for serverID in serverIDs :
            serverData = self.__dbConnector.getVMServerConfiguration(serverID)
            self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)