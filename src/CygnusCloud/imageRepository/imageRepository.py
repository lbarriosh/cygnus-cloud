# -*- coding: utf8 -*-
'''
Created on Apr 21, 2013

@author: luis
'''

from network.manager.networkManager import NetworkCallback, NetworkManager
from ccutils.dataStructures.multithreadingCounter import MultithreadingCounter
from database.imageRepository.imageRepositoryDB import ImageRepositoryDBConnector
from packets import ImageRepositoryPacketHandler, PACKET_T

class ImageRepository(object):
    
    def __init__(self, workingDirectory, uploadSlots, downloadSlots):
        self.__workingDirectory = workingDirectory
        self.__uploadSlots = uploadSlots
        self.__downloadSlots = downloadSlots
        
    def connectToDatabases(self, repositoryDBName, repositoryDBUser, repositoryDBPassword):
        self.__dbConnector = ImageRepositoryDBConnector(repositoryDBUser, repositoryDBPassword, repositoryDBName)
        self.__dbConnector.connect()
        
    def startListenning(self, certificatesDirectory, commandsListenningPort, dataListenningPort):
        self.__listenningPort = commandsListenningPort
        self.__dataListenningPort = dataListenningPort
        self.__networkManager = NetworkManager(certificatesDirectory)
        pHandler = ImageRepositoryPacketHandler(self.__networkManager)
        self.__commandsCallback = CommandsCallback(self.__workingDirectory, self.__networkManager, pHandler, self.__uploadSlots, self.__downloadSlots)
        self.__dataCallback = DataCallback(self.__workingDirectory)        
        self.__networkManager.startNetworkService()
        self.__networkManager.listenIn(commandsListenningPort, self.__commandsCallback, True)
        self.__networkManager.listenIn(dataListenningPort, self.__dataCallback, False) # TODO: añadir parámetro para configurar esto
        
    def stopListenning(self):
        self.__dataCallback.halt()
        self.__networkManager.stopNetworkService()
        self.__dbConnector.disconnect()
        
    def hasFinished(self):
        return self.__commandsCallback.finish()
        
class CommandsCallback(NetworkCallback):
    def __init__(self, workingDirectory, networkManager, pHandler, uploadSlots, downloadSlots):
        self.__networkManager = networkManager
        self.__pHandler = pHandler
        self.__workingDirectory = workingDirectory
        self.__uploadSlots = uploadSlots
        self.__uploadTransfers = MultithreadingCounter()
        self.__downloadSlots = downloadSlots
        self.__downloadTransfers = MultithreadingCounter()       
        self.__finish = False
        
    def processPacket(self, packet):
        data = self.__pHandler.readPacket(packet)
        if (data["packet_type"] == PACKET_T.HALT):
            self.__finish = True
    
    def finish(self):
        return self.__finish
    
class DataCallback(NetworkCallback):
    def __init__(self, workingDirectory):
        self.__workingDirectory = workingDirectory
        
    def halt(self):
        pass
        
    def processPacket(self, packet):
        pass    