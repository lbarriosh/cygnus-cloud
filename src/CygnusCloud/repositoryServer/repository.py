#coding=utf-8

from ccutils.dataStructures.multithreadingList import GenericThreadSafeList
from network.manager.networkManager import NetworkManager, NetworkCallback
from clusterServer.networking.packets import ClusterServerPacketHandler, MAIN_SERVER_PACKET_T
from virtualMachineServer.packets import VMServerPacketHandler, VM_SERVER_PACKET_T
from repositoryServer.packet import RepositoryPacketHandler
from repositoryServer.queue import WaitQueue
from database.repository.repositoryDB import RepositoryDatabaseConnector
import os

class ClusterServerPacketProcessor(NetworkCallback):
    def __init__(self, processor):
        self.__processor = processor
    def processClusterServerIncomingPacket(self, packet):
        self.__processor.processVMServerIncomingPacket(packet)

class VirtualMachineServerPacketProcessor(NetworkCallback):
    def __init__(self, processor):
        self.__processor = processor
    def processVirtualMachineServerIncomingPacket(self, packet):
        self.__processor.processVMServerIncomingPacket(packet)

class Repository(ClusterServerPacketProcessor, VirtualMachineServerPacketProcessor):
    
    def __init__(self, configurator):
        self.__downQueue = GenericThreadSafeList()
        self.__upQueue = GenericThreadSafeList()
        self.__configurator = configurator
        self.__connectDB(configurator.getConstant("databaseName"),
                         configurator.getConstant("databaseUserName"),
                         configurator.getConstant("databasePassword"))

    def __connectDB(self, dbName, dbUser, dbPassword):
        self.__dbConnector = RepositoryDatabaseConnector(dbUser, dbPassword, dbName)
        self.__dbConnector.connect()

    def startListenning(self, certificatePath, port):
        self.__downQueueThread = WaitQueue(self.__downQueue, '''TODO: Falta acceder a la función para saber si hay hueco de bajada''', self.__sendFreeDownSlot)
        self.__upQueueThread = WaitQueue(self.__upQueue, '''TODO: Falta acceder a la función para saber si hay hueco de subida''', self.__sendFreeUpSlot)
        self.__networkManager = NetworkManager(self.__configurator.getConstant("certificatePath"))
        
        self.__listenPort = self.__configurator.getConstant("listenningPort")
        self.__networkManager.startNetworkService()
        self.__clusterServerPacketHandler = ClusterServerPacketHandler(self.__networkManager)
        self.__vmServerPacketHandler = VMServerPacketHandler(self.__networkManager)
        self.__repositoryPacketHandler = RepositoryPacketHandler()
        clusterCallback = ClusterServerPacketProcessor(self)
        self.__networkManager.listenIn(port, clusterCallback, True)
        self.__virtualMachineCallback = VirtualMachineServerPacketProcessor(self)

    def processClusterServerIncomingPacket(self, packet):
        dataPacket = self.__clusterServerPacketHandler.readPacket(packet)
        if (dataPacket["packet_type"] == MAIN_SERVER_PACKET_T.DELETE_IMAGE) :
            self.__deleteImage(dataPacket)
            
    def processVirtualMachineServerIncomingPacket(self, packet):
        dataPacket = self.__vmServerPacketHandler.readPacket(packet)
        if (dataPacket["packet_type"] == VM_SERVER_PACKET_T.REQUEST_DOWNLOAD_SLOT) :
            self.__requestDownload(dataPacket)
        elif (dataPacket["packet_type"] == VM_SERVER_PACKET_T.REQUEST_UPLOAD_SLOT) :
            self.__requestUpload(dataPacket)

    def __deleteImage(self, data):
        imageID = data["ImageID"]
        imageInfo = self.__dbConnector.getImage(imageID)
        compressImagePath = self.__configurator.getConstant("compressFilesPath") + imageInfo["compressImagePath"]
        self.__dbConnector.removeImage(imageID)
        os.remove(compressImagePath)

    def __requestUpload(self, data):
        """
        data diccionario con:
            IP: dirección a la que contestar cuando haya hueco
            port: puerto al que enviar el aviso
            requestID: identificar único para ese cliente
        """
        self.__upQueue.append(data)
        p = self.__repositoryPacketHandler.createAcceptedPetition(data["requestID"])
        #TODO: Cambiar a modo unicast
        self.__networkManager.sendPacket('', self.__listenPort, p, data["IP"], data["requestID"])
        
    def __requestDownload(self, data):
        """
        data diccionario con:
            IP: dirección a la que contestar cuando haya hueco
            port: puerto al que enviar el aviso
            requestID: identificar único para ese cliente
        """
        self.__downQueue.append(data)
        p = self.__repositoryPacketHandler.createAcceptedPetition(data["requestID"])
        #TODO: Cambiar a modo unicast
        self.__networkManager.sendPacket('', self.__listenPort, p, data["IP"], data["requestID"])
        
        
    def __sendFreeUpSlot(self, data):
        """
        data diccionario con:
            IP: dirección a la que enviar el aviso
            port: puerto al que enviar el aviso
            requestID: identificar único para ese cliente
        """
        p = self.__repositoryPacketHandler.createUploadSlotPacket(data["requestID"])
        #TODO: Cambiar a modo unicast
        self.__networkManager.sendPacket('', self.__listenPort, p, data["IP"], int(data["port"]))
                
    def __sendFreeDownSlot(self, data):
        """
        data diccionario con:
            IP: dirección a la que enviar el aviso
            port: puerto al que enviar el aviso
            requestID: identificar único para ese cliente
        """
        p = self.__repositoryPacketHandler.createDownloadSlotPacket(data["requestID"])
        #TODO: Cambiar a modo unicast
        self.__networkManager.sendPacket('', self.__listenPort, p, data["IP"], int(data["port"]))
        
        
        
        
        
        
