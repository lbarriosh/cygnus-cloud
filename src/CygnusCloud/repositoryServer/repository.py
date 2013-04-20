#coding=utf-8

from ccutils.dataStructures.multithreadingList import GenericThreadSafeList
from network.manager.networkManager import NetworkManager, NetworkCallback
from clusterServer.networking.packets import ClusterServerPacketHandler, MAIN_SERVER_PACKET_T
from virtualMachineServer.packets import VMServerPacketHandler, VM_SERVER_PACKET_T
from database.repository.repositoryDB import RepositoryDatabaseConnector
import os

class ClusterServerPacketProcessor(NetworkCallback):
    def __init__(self, processor):
        self.__processor = processor
    def processClusterServerIncomingPacket(self, packet):
        self.__processor.processVMServerIncomingPacket(packet)

class Repository(ClusterServerPacketProcessor):
    
    def __init__(self, configurator):
        self.__sendQueue = GenericThreadSafeList()
        self.__configurator = configurator
        self.__connectDB(configurator.getConstant("databaseName"),
                         configurator.getConstant("databaseUserName"),
                         configurator.getConstant("databasePassword"))

    def __connectDB(self, dbName, dbUser, dbPassword):
        self.__dbConnector = RepositoryDatabaseConnector(dbUser, dbPassword, dbName)
        self.__dbConnector.connect()

    def startListenning(self, certificatePath, port):
        self.__networkManager = NetworkManager(self.__configurator.getConstant("certificatePath"))
        
        self.__listenPort = self.__configurator.getConstant("listenningPort")
        self.__networkManager.startNetworkService()
        self.__clusterServerPacketHandler = ClusterServerPacketHandler(self.__networkManager)
        self.__vmServerPacketHandler = VMServerPacketHandler(self.__networkManager)
        clusterCallback = ClusterServerPacketProcessor(self)
        self.__networkManager.listenIn(port, clusterCallback, True)

    def processClusterServerIncomingPacket(self, packet):
        dataPacket = self.__clusterServerPacketHandler.readPacket(packet)
        if (dataPacket["packet_type"] == MAIN_SERVER_PACKET_T.DELETE_IMAGE) :
            self.__deleteImage(dataPacket)
        elif (dataPacket["packet_type"] == VM_SERVER_PACKET_T.SET_IMAGE) :
            self.__recievedImage(dataPacket)

    def __deleteImage(self, data):
        imageID = data["ImageID"]
        imageInfo = self.__dbConnector.getImage(imageID)
        compressImagePath = self.__configurator.getConstant("compressFilesPath") + imageInfo["compressImagePath"]
        self.__dbConnector.removeImage(imageID)
        os.remove(compressImagePath)

    def __recievedImage(self, data):
        self.__dbConnector.addImage(data["ImageID"], data["Filename"], data["GroupID"])
        
        
        
        
        
        
        
        
