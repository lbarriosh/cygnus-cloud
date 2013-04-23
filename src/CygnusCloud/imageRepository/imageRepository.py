# -*- coding: utf8 -*-
'''
Created on Apr 21, 2013

@author: luis
'''

from network.manager.networkManager import NetworkCallback, NetworkManager
from database.imageRepository.imageRepositoryDB import ImageRepositoryDBConnector, IMAGE_STATUS_T
from packets import ImageRepositoryPacketHandler, PACKET_T
from network.ftp.ftpServer import ConfigurableFTPServer, FTPCallback

class ImageRepository(object):
    
    def __init__(self, workingDirectory):
        self.__workingDirectory = workingDirectory
        
    def connectToDatabases(self, repositoryDBName, repositoryDBUser, repositoryDBPassword):
        self.__dbConnector = ImageRepositoryDBConnector(repositoryDBUser, repositoryDBPassword, repositoryDBName)
        self.__dbConnector.connect()
        
    def startListenning(self, networkInterface, certificatesDirectory, commandsListenningPort, dataListenningPort, maxConnections,
                        maxConnectionsPerIP, uploadBandwidthRatio, downloadBandwidthRatio):       
        self.__networkManager = NetworkManager(certificatesDirectory)
        pHandler = ImageRepositoryPacketHandler(self.__networkManager)
        
        self.__commandsCallback = CommandsCallback(self.__workingDirectory, self.__networkManager, pHandler, commandsListenningPort, self.__dbConnector)        
        
        self.__networkManager.startNetworkService()
        self.__networkManager.listenIn(commandsListenningPort, self.__commandsCallback, True)
        
        dataCallback = DataCallback()
        self.__ftpServer = ConfigurableFTPServer("Image repository FTP Server")
        self.__ftpServer.startListenning(networkInterface, dataListenningPort, maxConnections, maxConnectionsPerIP, dataCallback, downloadBandwidthRatio, uploadBandwidthRatio)
        
    def stopListenning(self):
        self.__ftpServer.stopListenning()
        self.__networkManager.stopNetworkService()
        self.__dbConnector.disconnect()
        
    def hasFinished(self):
        return self.__commandsCallback.finish()
        
class CommandsCallback(NetworkCallback):
    def __init__(self, workingDirectory, networkManager, pHandler, commandsListenningPort, dbConnector):
        self.__networkManager = networkManager
        self.__pHandler = pHandler
        self.__commandsListenningPort = commandsListenningPort
        self.__workingDirectory = workingDirectory    
        self.__dbConnector = dbConnector    
        self.__finish = False
        
    def processPacket(self, packet):
        data = self.__pHandler.readPacket(packet)
        if (data["packet_type"] == PACKET_T.HALT):
            self.__finish = True
        elif (data["packet_type"] == PACKET_T.ADD_IMAGE):
            self.__addNewImage(data)
        elif (data["packet_type"] == PACKET_T.RETR_REQUEST):
            self.__handleRetrieveRequest(data)
    
    def finish(self):
        return self.__finish
    
    def __addNewImage(self, data):
        imageID = self.__dbConnector.addImage()
        p = self.__pHandler.createAddedImagePacket(imageID)
        self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        
    def __handleRetrieveRequest(self, data):
        imageData = self.__dbConnector.getImageData(data["imageID"])
        if (imageData == None) :
            p = self.__pHandler.createErrorPacket(PACKET_T.RETR_REQUEST_ERROR, "The image {0} does not exist".format(data["imageID"]))
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        elif (imageData["imageStatus"] != IMAGE_STATUS_T.READY) :
            p = self.__pHandler.createErrorPacket(PACKET_T.RETR_REQUEST_ERROR, "The image {0} is already being edited".format(data["imageID"]))
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        else:
            p = self.__pHandler.createImageRequestReceivedPacket(PACKET_T.RETR_REQUEST_RECVD)
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
            # TODO: encolar
        
class DataCallback(FTPCallback):
    def on_disconnect(self):
        pass

    def on_login(self, username):
        pass
    
    def on_logout(self, username):
        pass
    
    def on_f_sent(self, f):
        pass
    
    def on_f_received(self, f):
        pass
    
    def on_incomplete_f_sent(self, f):
        pass
    
    def on_incomplete_f_received(self, f):
        pass