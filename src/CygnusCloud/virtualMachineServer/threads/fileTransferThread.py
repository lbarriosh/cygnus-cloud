# -*- coding: utf8 -*-
'''
Created on Apr 28, 2013

@author: luis
'''

from ccutils.threads import QueueProcessingThread
from network.manager.networkManager import NetworkCallback
from network.ftp.ftpClient import FTPClient
from imageRepository.packets import ImageRepositoryPacketHandler, PACKET_T as IR_PACKET_T
from virtualMachineServer.networking.packets import VM_SERVER_PACKET_T
from time import sleep

class FileTransferThread(QueueProcessingThread):
    def __init__(self, networkManager, serverListeningPort, packetHandler,
                 queue, compressionQueue, imageDirectory, ftpTimeout, ):
        QueueProcessingThread.__init__(self, "File transfer thread", queue)
        self.__networkManager = networkManager
        self.__serverListeningPort = serverListeningPort
        self.__workingDirectory = imageDirectory
        self.__repositoryPacketHandler = ImageRepositoryPacketHandler(self.__networkManager)
        self.__vmServerPacketHandler = packetHandler
        self.__ftpTimeout = ftpTimeout
        self.__compressionQueue = compressionQueue
        
    def processElement(self, data):
        try :
            # Nos conectamos al repositorio
            callback = _FileTransferCallback(self.__repositoryPacketHandler, self.__workingDirectory, data["repositoryIP"], self.__ftpTimeout)
            self.__networkManager.connectTo(data["repositoryIP"], data["repositoryPort"], 
                                            self.__ftpTimeout, callback)
            while not self.__networkManager.isConnectionReady(data["repositoryIP"], data["repositoryPort"]) :
                sleep(0.1)
           
            # Solicitamos el inicio de la transferencia
            if (data["retrieve"]) :
                p = self.__repositoryPacketHandler.createRetrieveRequestPacket(data["sourceImageID"], data["modify"])
            else :
                p = None # TODO: meter store aquí
            self.__networkManager.sendPacket(data["repositoryIP"], data["repositoryPort"], p)
            
            # Esperamos a que la transferencia termine
            while not callback.isOperationCompleted() :
                sleep(0.1)
            if (callback.getErrorMessage() != None) :
                # Error => informamos al usuario                
                p = self.__vmServerPacketHandler.createErrorPacket(VM_SERVER_PACKET_T.IMAGE_EDITION_ERROR, 
                                                                   callback.getErrorMessage(), 
                                                                   data["CommandID"])
                self.__networkManager.sendPacket('', self.__serverListeningPort, p)
            
            
            # Pedimos un ID de imagen al repositorio (sólo si es necesario)
            if (data["retrieve"]) :
                self.__networkManager.sendPacket('', self.__repositoryPacketHandler.createAddImagePacket())
                while not callback.isOperationCompleted() :
                    sleep(0.1)
                data["ImageID"] = callback.getDomainImageID()
                
            # Nos desconectamos del repositorio
            self.__networkManager.closeConnection(data["repositoryIP"], data["repositoryPort"])
            
            # No error => añadimos el fichero a la cola de descompresión
            self.__compressionQueue.queue(data)
        except Exception as e :
            p = self.__vmServerPacketHandler.createErrorPacket(VM_SERVER_PACKET_T.IMAGE_EDITION_ERROR, 
                                                                   "Unable to connect to the image repository" + e.message, 
                                                                   data["CommandID"])
            self.__networkManager.sendPacket('', self.__serverListeningPort, p)
        
class _FileTransferCallback(NetworkCallback):
    
    def __init__(self, packetHandler, imageDirectory, ftpServerIP, ftpTimeout):
        self.__repositoryPacketHandler = packetHandler
        self.__operation_completed = False
        self.__errorMessage = None
        self.__workingDirectory = imageDirectory
        self.__ftpServerIP = ftpServerIP
        self.__ftpTimeout = ftpTimeout
        self.__imageID = None
        
    def isOperationCompleted(self):
        return self.__operation_completed
    
    def getErrorMessage(self):
        return self.__errorMessage
    
    def getDomainImageID(self):
        return self.__imageID
    
    def processPacket(self, packet):
        data = self.__repositoryPacketHandler.readPacket(packet)
        if (data["packet_type"] == IR_PACKET_T.RETR_REQUEST_RECVD or
            data["packet_type"] == IR_PACKET_T.STOR_REQUEST_RECVD) :
            return
        elif (data["packet_type"] == IR_PACKET_T.RETR_REQUEST_ERROR or data["packet_type"] == IR_PACKET_T.RETR_ERROR) :
            self.__errorMessage = "Retrieve error: " + data["errorMessage"]
        elif (data["packet_type"] == IR_PACKET_T.STOR_REQUEST_ERROR or data["packet_type"] == IR_PACKET_T.STOR_ERROR) :
            self.__errorMessage = "Store error: " + data["errorMessage"]
        elif (data["packet_type"] == IR_PACKET_T.RETR_START) :
            try :
                ftpClient = FTPClient()
                ftpClient.connect(self.__ftpServerIP, data['FTPServerPort'], self.__ftpTimeout, data['username'], data['password'])
                ftpClient.retrieveFile(data['fileName'], self.__workingDirectory, data['serverDirectory']) 
                ftpClient.disconnect()
            except Exception as e:
                self.__errorMessage = e.message                  
        elif (data["packet_type"] == IR_PACKET_T.ADDED_IMAGE_ID):
            self.__imageID = data["addedImageID"]
        
        self.__operation_completed = True   