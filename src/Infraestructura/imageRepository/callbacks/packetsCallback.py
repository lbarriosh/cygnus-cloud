# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: packetsCallback.py    
    Version: 3.0
    Description: image repository packet callback
    
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

from network.manager.networkManager import NetworkCallback
from imageRepository.database.image_status_t import IMAGE_STATUS_T
from imageRepository.packetHandling.packet_t import PACKET_T
from errors.codes import ERROR_DESC_T
from ccutils.processes.childProcessManager import ChildProcessManager
from os import path, statvfs

class CommandsCallback(NetworkCallback):
    """
    These objects process the request received through the control connection
    """    
    def __init__(self, networkManager, pHandler, listenningPort, dbConnector, retrieveQueue, storeQueue, diskImagesDirectory):
        """
        Initializes the callback's state
        Args:
            networkManager: a NetworkManager object
            pHandler: a packet handler
            listenningPort: the control's connection port
            dbConnector: a database connection
            retrieveQueue: a retrieve requests queue
            storeQueue: a store requests queue    
        """
        self.__networkManager = networkManager
        self.__repositoryPacketHandler = pHandler
        self.__commandsListenningPort = listenningPort
        self.__dbConnector = dbConnector    
        self.__haltReceived = False
        self.__retrieveQueue = retrieveQueue
        self.__storeQueue = storeQueue
        self.__diskImagesDirectory = diskImagesDirectory
        
    def processPacket(self, packet):
        """
        Processes an incoming packet
        Args:
            packet: the incoming packet
        Returns:
            Nothing
        """
        data = self.__repositoryPacketHandler.readPacket(packet)
        if (data["packet_type"] == PACKET_T.HALT):
            self.__haltReceived = True
        elif (data["packet_type"] == PACKET_T.ADD_IMAGE):
            self.__addNewImage(data)
        elif (data["packet_type"] == PACKET_T.RETR_REQUEST):
            self.__handleRetrieveRequest(data)    
        elif (data["packet_type"] == PACKET_T.STOR_REQUEST):
            self.__handleStorRequest(data)
        elif (data["packet_type"] == PACKET_T.DELETE_REQUEST):
            self.__deleteImage(data)
        elif (data["packet_type"] == PACKET_T.STATUS_REQUEST):
            self.__sendStatusData(data)
        elif (data["packet_type"] == PACKET_T.CANCEL_EDITION):
            self.__cancelImageEdition(data)
            
    def __cancelImageEdition(self, data):
        """
        Unlocks an image
        Args:
            data: the received packet's content
        Returns:
            Nothing
        """
        self.__dbConnector.cancelImageEdition(data["ImageID"])
        p = self.__repositoryPacketHandler.createImageRequestReceivedPacket(PACKET_T.IMAGE_EDITION_CANCELLED)
        self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data["clientIP"], data["clientPort"])
            
    def __sendStatusData(self, data):
        """
        Sends the status data to the cluster server
        Args:
            data: the received packet's content
        Returns:
            Nothing
        """
        diskStats = statvfs(self.__diskImagesDirectory)
        freeDiskSpace = diskStats.f_bfree * diskStats.f_frsize / 1024
        totalDiskSpace = diskStats.f_blocks * diskStats.f_frsize / 1024
        p = self.__repositoryPacketHandler.createStatusDataPacket(freeDiskSpace, totalDiskSpace)
        self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
    
    def __addNewImage(self, data):
        """
        Registers a new image ID
        Args:
            data: the received packet's content
        Returns:
            Nothing
        """
        imageID = self.__dbConnector.addImage()
        p = self.__repositoryPacketHandler.createAddedImagePacket(imageID)        
        value = self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        if (value != None) :
            self.__dbConnector.deleteImage(imageID)
     
    def __handleRetrieveRequest(self, data):
        """
        Handles a FTP RETR request packet
        Args:
            data: the received packet's content
        Returns:
            Nothing
        """   
        imageData = self.__dbConnector.getImageData(data["imageID"])
        if (imageData == None) :
            p = self.__repositoryPacketHandler.createErrorPacket(PACKET_T.RETR_REQUEST_ERROR, ERROR_DESC_T.IR_UNKNOWN_IMAGE)
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        elif (imageData["imageStatus"] != IMAGE_STATUS_T.READY) :
            p = self.__repositoryPacketHandler.createErrorPacket(PACKET_T.RETR_REQUEST_ERROR, ERROR_DESC_T.IR_IMAGE_EDITED)
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        else:
            # No errors => queue the request and answer
            p = self.__repositoryPacketHandler.createImageRequestReceivedPacket(PACKET_T.RETR_REQUEST_RECVD)
            value = self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
            if (value == None) :    
                self.__retrieveQueue.append((data["imageID"], data["clientIP"], data["clientPort"]))
                if (data["modify"]) :
                    self.__dbConnector.changeImageStatus(data["imageID"], IMAGE_STATUS_T.EDITION)
    
    def __handleStorRequest(self, data):
        """
        Handles a FTP STOR request packe
        Args:
            data: the received packet's content
        Returns:
            Nothing
        """   
        imageData = self.__dbConnector.getImageData(data["imageID"])
        if (imageData == None) :
            p = self.__repositoryPacketHandler.createErrorPacket(PACKET_T.STOR_REQUEST_ERROR, ERROR_DESC_T.IR_UNKNOWN_IMAGE)
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        elif not (imageData["imageStatus"] == IMAGE_STATUS_T.EDITION or imageData["imageStatus"] == IMAGE_STATUS_T.NOT_RECEIVED) :
            p = self.__repositoryPacketHandler.createErrorPacket(PACKET_T.STOR_REQUEST_ERROR, ERROR_DESC_T.IR_NOT_EDITED_IMAGE)
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        else:
            # No errors => queue the request and answer
            p = self.__repositoryPacketHandler.createImageRequestReceivedPacket(PACKET_T.STOR_REQUEST_RECVD)
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])            
            self.__storeQueue.append((data["imageID"], data["clientIP"], data["clientPort"]))        
            
    def __deleteImage(self, data):
        """
        Handles an image deletion request
        Args:
            data: the received packet's content
        Returns:
            Nothing
        """  
        imageData = self.__dbConnector.getImageData(data["imageID"])
        if (imageData == None) :
            p = self.__repositoryPacketHandler.createImageDeletionErrorPacket(data["imageID"], ERROR_DESC_T.IR_UNKNOWN_IMAGE)
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        elif (imageData["imageStatus"] == IMAGE_STATUS_T.EDITION):
            p = self.__repositoryPacketHandler.createImageDeletionErrorPacket(data["imageID"], ERROR_DESC_T.IR_IMAGE_EDITED)
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        else :            
            if (not "undefined" in imageData["compressedFilePath"]) :
                imageDirectory = path.dirname(imageData["compressedFilePath"])
                ChildProcessManager.runCommandInForeground("rm -rf " + imageDirectory, Exception)
            self.__dbConnector.deleteImage(data["imageID"]) # TODO: poner encima del if
            p = self.__repositoryPacketHandler.createDeleteRequestReceivedPacket(data["imageID"])
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])            
        
    def haltReceived(self):
        """
        Checks if a halt packet has been received
        Args:
            None
        Returns:
            True if a halt packet was received, and False otherwise
        """   
        return self.__haltReceived