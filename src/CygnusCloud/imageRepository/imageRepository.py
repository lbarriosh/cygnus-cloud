# -*- coding: utf8 -*-
'''
Created on Apr 21, 2013

@author: luis
'''

from network.manager.networkManager import NetworkCallback, NetworkManager
from database.imageRepository.imageRepositoryDB import ImageRepositoryDBConnector, IMAGE_STATUS_T
from packets import ImageRepositoryPacketHandler, PACKET_T
from network.ftp.ftpServer import ConfigurableFTPServer, FTPCallback
from ccutils.dataStructures.multithreadingList import GenericThreadSafeList
from ccutils.dataStructures.multithreadingCounter import MultithreadingCounter
from os import remove, path
from time import sleep
from re import sub
from ccutils.processes.childProcessManager import ChildProcessManager

class ImageRepository(object):
    
    def __init__(self, workingDirectory):
        self.__workingDirectory = workingDirectory        
        self.__slotCounter = MultithreadingCounter()
        self.__retrieveQueue = GenericThreadSafeList()
        
    def connectToDatabases(self, repositoryDBName, repositoryDBUser, repositoryDBPassword):
        self.__dbConnector = ImageRepositoryDBConnector(repositoryDBUser, repositoryDBPassword, repositoryDBName)
        self.__dbConnector.connect()
        
    def startListenning(self, networkInterface, certificatesDirectory, commandsListenningPort, dataListenningPort, maxConnections,
                        maxConnectionsPerIP, uploadBandwidthRatio, downloadBandwidthRatio): 
        self.__maxConnections = maxConnections      
        self.__commandsListenningPort = commandsListenningPort
        self.__dataListenningPort = dataListenningPort
        self.__networkManager = NetworkManager(certificatesDirectory)
        self.__pHandler = ImageRepositoryPacketHandler(self.__networkManager)        
        
        self.__commandsCallback = CommandsCallback(self.__workingDirectory, self.__networkManager, self.__pHandler, commandsListenningPort, self.__dbConnector,
                                                   self.__retrieveQueue)        
        
        self.__networkManager.startNetworkService()
        self.__networkManager.listenIn(commandsListenningPort, self.__commandsCallback, True)
        
        dataCallback = DataCallback(self.__slotCounter, self.__dbConnector, self.__onClientLogout)
        self.__ftpServer = ConfigurableFTPServer("Image repository FTP Server")
        self.__ftpServer.startListenning(networkInterface, dataListenningPort, maxConnections, maxConnectionsPerIP, 
                                         None, downloadBandwidthRatio, uploadBandwidthRatio)
        
    def stopListenning(self):
        self.__ftpServer.stopListenning()
        self.__networkManager.stopNetworkService()
        self.__dbConnector.disconnect()
        
    def doTransfers(self):
        while not self.__commandsCallback.finish():
            if (self.__slotCounter.read() == self.__maxConnections) :
                sleep(0.1)
            else :
                self.__slotCounter.decrement()
                if( not self.__retrieveQueue.isEmpty()) :
                    (imageID, clientIP, clientPort) = self.__retrieveQueue.pop(0)
                    username = "user" + sub("[\\.]", "", clientIP) + str(clientPort)
                    password = ChildProcessManager.runCommandInForeground("openssl rand -base64 20", Exception)
                    compressedFilePath = self.__dbConnector.getImageData(imageID)["compressedFilePath"]
                    homeDirectory = path.dirname(path.abspath(compressedFilePath))
                    self.__ftpServer.addUser(username, password, homeDirectory, "elradfmwM")
                    
                    p = self.__pHandler.createTransferEnabledPacket(PACKET_T.RETR_START, imageID, self.__dataListenningPort, 
                                                                        username, password, path.basename(compressedFilePath))
                    self.__networkManager.sendPacket('', self.__commandsListenningPort, p, clientIP, clientPort)
    
    def __onClientLogout(self, username):
        self.__ftpServer.removeUser(username)
        
class CommandsCallback(NetworkCallback):
    def __init__(self, workingDirectory, networkManager, pHandler, commandsListenningPort, dbConnector, retrieveQueue):
        self.__networkManager = networkManager
        self.__pHandler = pHandler
        self.__commandsListenningPort = commandsListenningPort
        self.__workingDirectory = workingDirectory    
        self.__dbConnector = dbConnector    
        self.__finish = False
        self.__retrieveQueue = retrieveQueue
        
    def processPacket(self, packet):
        data = self.__pHandler.readPacket(packet)
        if (data["packet_type"] == PACKET_T.HALT):
            self.__finish = True
        elif (data["packet_type"] == PACKET_T.ADD_IMAGE):
            self.__addNewImage(data)
        elif (data["packet_type"] == PACKET_T.RETR_REQUEST):
            self.__handleRetrieveRequest(data)    
    
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
            self.__retrieveQueue.append((data["imageID"], data["clientIP"], data["clientPort"]))
            if (data["modify"]) :
                self.__dbConnector.changeImageStatus(data["imageID"], IMAGE_STATUS_T.EDITION)
            
    def finish(self):
        return self.__finish
        
class DataCallback(FTPCallback):
    
    def __init__(self, slotCounter, dbConnector, onClientLogout):
        self.__slotCounter = slotCounter
        self.__dbConnector = dbConnector
        self.__onClientLogout = onClientLogout
    
    def on_disconnect(self):
        pass

    def on_login(self, username):
        pass
    
    def on_logout(self, username):
        self.__onClientLogout(username)
        self.__slotCounter.increment()
    
    def on_file_sent(self, f):
        pass
    
    def on_file_received(self, f):
        self.__dbConnector.processFinishedTransfer(f)
    
    def on_incomplete_file_sent(self, f):
        self.__slotCounter.increment()
    
    def on_incomplete_f_received(self, f):
        self.__slotCounter.increment()
        remove(f)