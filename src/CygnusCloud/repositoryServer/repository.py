#coding=utf-8

from ccutils.dataStructures.multithreadingList import GenericThreadSafeList
from ccutils.dataStructures.multithreadingCounter import MultithreadingCounter
from ccutils.threads import QueueProcessingThread
from network.manager.networkManager import NetworkManager, NetworkCallback
from clusterServer.networking.packets import ClusterServerPacketHandler, MAIN_SERVER_PACKET_T
from virtualMachineServer.packets import VMServerPacketHandler, VM_SERVER_PACKET_T
from database.repository.repositoryDB import RepositoryDatabaseConnector
from repositoryServer.packet import RepositoryPacketHandler
from ftplib import FTP
import os
from time import sleep

class ClusterServerPacketProcessor(NetworkCallback):
    def __init__(self, processor):
        self.__processor = processor
    def processClusterServerIncomingPacket(self, packet):
        self.__processor.processVMServerIncomingPacket(packet)
    
class VMServerPacketProcessor(NetworkCallback):
    def __init__(self, processor):
        self.__processor = processor
    def processVMServerIncomingPacket(self, packet):
        self.__processor.processVMServerIncomingPacket(packet)

class SendThread(QueueProcessingThread):
    
    def __init__(self, name, queue, networkManager, maxFiles):
        QueueProcessingThread.__init__(self, name, queue)
        self.__counter = MultithreadingCounter()
        self.__maxTransferFile = maxFiles
        self.__networkManager = networkManager
        self.__repositoryPacketHandler = RepositoryPacketHandler(self.__networkManager)

    def processElement(self, element):
        while (not self.__counter.incrementIfLessThan(self.__maxTransferFile)) :
            sleep(10)
        # Enviamos el archivo
        compressFile = open(element["compressImagePath"], "r")
        ftp = FTP(element["host"])
        ftp.login()
        ftp.storbinary("STOR " + compressFile.filename, compressFile)
        compressFile.close()
        
        # Avisamos al servidor de máquinas virtuales
        self.__repositoryPacketHandler.createImageSendPacket(element["SendID"])

class Repository(ClusterServerPacketProcessor, VMServerPacketProcessor):
    
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
        
        self.__sendThread = SendThread("sendThread", self.__sendQueue, 
                                           self.__networkManager, 
                                           self.__configurator.getConstant("maxFiles"))
        
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

    def processVMServerIncomingPacket(self, packet):
        dataPacket = self.__vmServerPacketHandler.readPacket(packet)
        if (dataPacket["packet_type"] == VM_SERVER_PACKET_T.GET_IMAGE) :
            self.__sendImage(dataPacket)
        elif (dataPacket["packet_type"] == VM_SERVER_PACKET_T.SET_IMAGE) :
            self.__recievedImage(dataPacket)

    def __deleteImage(self, data):
        imageID = data["ImageID"]
        imageInfo = self.__dbConnector.getImage(imageID)
        compressImagePath = self.__configurator.getConstant("compressFilesPath") + imageInfo["compressImagePath"]
        self.__dbConnector.removeImage(imageID)
        os.remove(compressImagePath)

    def __sendImage(self, data):
        imageID = data["ImageID"]
        imageInfo = self.__dbConnector.getImage(imageID)
        dataSend = dict()
        dataSend["SendID"] = data["SendID"]
        dataSend["compressImagePath"] = self.__configurator.getConstant("compressFilesPath") + imageInfo["compressImagePath"]
        self.__sendQueue.append(dataSend)

    def __recievedImage(self, data):
        self.__dbConnector.addImage(data["ImageID"], data["Filename"], data["GroupID"])
        
        
        
        
        
        
        
        
