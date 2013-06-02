# -*- coding: utf8 -*-
'''
Created on May 10, 2013

@author: luis
'''

from imageRepository.packetHandling.packet_t import PACKET_T
from clusterServer.packetHandling.packet_t import CLUSTER_SERVER_PACKET_T
from clusterServer.database.image_state_t import IMAGE_STATE_T

class ImageRepositoryPacketReactor(object):
    
    def __init__(self, dbConnector, networkManager, listenningPort, 
                 repositoryIP, repositoryPort, webPacketHandler, vmServerPacketHandler, imageRepositoryPacketHandler):
        self.__dbConnector = dbConnector
        self.__networkManager = networkManager
        self.__listenningPort = listenningPort
        self.__repositoryIP = repositoryIP
        self.__repositoryPort = repositoryPort
        self.__packetHandler = webPacketHandler
        self.__vmServerPacketHandler = vmServerPacketHandler        
        self.__imageRepositoryPacketHandler = imageRepositoryPacketHandler
    
    def processImageRepositoryIncomingPacket(self, packet):
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
                # Borrar la imagen de los servidores
                self.__sendDeleteRequets(data['imageID'], commandID)
        elif data['packet_type'] == PACKET_T.DELETE_REQUEST_ERROR:            
            p = self.__packetHandler.createErrorPacket(CLUSTER_SERVER_PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR, data['errorDescription'], commandID)
            self.__networkManager.sendPacket('', self.__listenningPort, p)            
            
    def __sendDeleteRequets(self, imageID, commandID):
        # Borramos la imagen de todos los servidores de máquinas arrancados. Nos ocuparemos de los otros
        # a medida que se vayan arrancando
        p = self.__vmServerPacketHandler.createDeleteImagePacket(imageID, commandID)
        serverIDs = self.__dbConnector.getHosts(imageID, IMAGE_STATE_T.DELETE)
        for serverID in serverIDs :
            serverData = self.__dbConnector.getVMServerBasicData(serverID)
            self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)