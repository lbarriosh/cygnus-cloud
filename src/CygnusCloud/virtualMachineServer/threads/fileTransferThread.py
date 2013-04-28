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
                 transferQueue, compressionQueue, workingDirectory, ftpTimeout, ):
        QueueProcessingThread.__init__(self, "File transfer thread", transferQueue)
        self.__networkManager = networkManager
        self.__serverListeningPort = serverListeningPort
        self.__workingDirectory = workingDirectory
        self.__repositoryPacketHandler = ImageRepositoryPacketHandler(self.__networkManager)
        self.__vmServerPacketHandler = packetHandler
        self.__ftpTimeout = ftpTimeout
        self.__compressionQueue = compressionQueue
        
    def processElement(self, data):
        try :
            # Paso 1: nos conectamos al repositorio
            callback = _FileTransferCallback(self.__repositoryPacketHandler, self.__workingDirectory, data["repositoryIP"], self.__ftpTimeout)
            self.__networkManager.connectTo(data["repositoryIP"], data["repositoryPort"], 
                                            self.__ftpTimeout, callback)
            while not self.__networkManager.isConnectionReady(data["repositoryIP"], data["repositoryPort"]) :
                sleep(0.1)
            # Paso 2: solicitamos el inicio de la transferencia
            if (data["retrieve"]) :
                p = self.__repositoryPacketHandler.createRetrieveRequestPacket(data["sourceImageID"], data["modify"])
            else :
                p = None # TODO: meter store aquí
            self.__networkManager.sendPacket(data["repositoryIP"], data["repositoryPort"], p)
            # Esperamos a que la transferencia termine
            while not callback.hasTransferFinished() :
                sleep(0.1)
            if (callback.getErrorMessage() != None) :
                # Error => informamos al usuario                
                p = self.__vmServerPacketHandler.createErrorPacket(VM_SERVER_PACKET_T.IMAGE_EDITION_ERROR, 
                                                                   callback.getErrorMessage(), 
                                                                   data["CommandID"])
                self.__networkManager.sendPacket('', self.__serverListeningPort, p)
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
    
    def __init__(self, packetHandler, workingDirectory, ftpServerIP, ftpTimeout):
        self.__repositoryPacketHandler = packetHandler
        self.__transfer_finished = False
        self.__errorMessage = None
        self.__workingDirectory = workingDirectory
        self.__ftpServerIP = ftpServerIP
        self.__ftpTimeout = ftpTimeout
        
    def hasTransferFinished(self):
        return self.__transfer_finished
    
    def getErrorMessage(self):
        return self.__errorMessage
    
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
            
        self.__transfer_finished = True