'''
Created on Apr 21, 2013

@author: luis
'''

from network.manager.networkManager import NetworkCallback
from ccutils.dataStructures.multithreadingCounter import MultithreadingCounter


class ImageRepository(object):
    
    def __init__(self, networkManager, workingDirectory, uploadSlots, downloadSlots):
        self.__workingDirectory = workingDirectory
        self.__networkManager = networkManager
        self.__callback = CommandsCallback(workingDirectory, networkManager, uploadSlots, downloadSlots)
        
    def startListenning(self, commandsListenningPort, dataListenningPort):
        self.__listenningPort = commandsListenningPort
        self.__dataListenningPort = dataListenningPort
        self.__networkManager.listenIn(commandsListenningPort, self.__callback, True)
        self.__networkManager.listenIn(dataListenningPort, DataCallback(self.__workingDirectory))
        
    def stopListenning(self):
        self.__networkManager.closeConnection('', self.__listenningPort)
        
class CommandsCallback(NetworkCallback):
    def __init__(self, networkManager, uploadSlots, downloadSlots):
        self.__networkManager = networkManager
        self.__uploadSlots = uploadSlots
        self.__uploadTransfers = MultithreadingCounter()
        self.__downloadSlots = downloadSlots
        self.__downloadTransfers = MultithreadingCounter()
        
    def processPacket(self, packet):
        pass
    
class DataCallback(NetworkCallback):
    def __init__(self, workingDirectory):
        self.__workingDirectory = workingDirectory
        
    def processPacket(self, packet):
        pass
    