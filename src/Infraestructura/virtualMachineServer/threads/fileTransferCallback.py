# -*- coding: utf8 -*-
'''
Created on Jun 8, 2013

@author: luis
'''

from network.manager.networkManager import NetworkCallback
from ftp.ftpClient import FTPClient
from errors.codes import ERROR_DESC_T
from imageRepository.packetHandling.packet_t import PACKET_T as IR_PACKET_T

class FileTransferCallback(NetworkCallback):
    """
    Callback que usaremos para comunicarnos con el repositorio de imágenes
    """
    
    def __init__(self, packetHandler, workingDirectory, imageRepositoryIP, ftpTimeout, sourceFilePath=None):
        """
        Inicializa el estado del callback
        Argumentos:
            packetHandler: objeto que usaremos para leer y crear los paquetes que se intercambiarán con el repositorio
            workingDirectory: directorio en el que se almacenarán los ficheros .zip intercambiados con el repositorio
            imageRepositoryIP: la dirección IP del repositorio de imágenes
            ftpTimeout: el tiemout máximo para las comuncaciones con el servidor FTP
            sourceFilePath: la ruta del fichero a subir al repositorio. Sólo se usa en transferencias de tipo STORE.
        """
        self.__repositoryPacketHandler = packetHandler
        self.__operation_completed = False
        self.__errorDescription = None
        self.__workingDirectory = workingDirectory
        self.__ftpServerIP = imageRepositoryIP
        self.__ftpTimeout = ftpTimeout
        self.__imageID = None
        self.__sourceFilePath = sourceFilePath
        
    def isTransferCompleted(self):
        """
        Indica si la transferencia actual con el repositorio ha finalizado o no
        """
        return self.__operation_completed
    
    def getErrorDescription(self):
        """
        Devuelve un mensaje que describe el error que se ha producido durante
        la última transferencia
        """
        return self.__errorDescription
    
    def getDomainImageID(self):
        """
        Devuelve el identificador único de una imagen. El repositorio lo ha creado
        bajo petición expresa del hilo de transferencia.
        """
        return self.__imageID
    
    def prepareForNewTransfer(self):
        """
        Prepara el callback para una nueva transferencia
        """
        self.__errorDescription = None
        self.__operation_completed = False
        self.__image_not_found = False
        
    def getImageNotFound(self):
        return self.__image_not_found
    
    def processPacket(self, packet):
        """
        Procesa un paquete recibido desde el repositorio de imágenes.
        Argumentos:
            packet: el paquete a procesar
        Devuelve:
            Nada
        """
        data = self.__repositoryPacketHandler.readPacket(packet)
        if (data["packet_type"] == IR_PACKET_T.RETR_REQUEST_RECVD or
            data["packet_type"] == IR_PACKET_T.STOR_REQUEST_RECVD) :
            return
        elif (data["packet_type"] == IR_PACKET_T.RETR_REQUEST_ERROR or data["packet_type"] == IR_PACKET_T.RETR_ERROR or
              data["packet_type"] == IR_PACKET_T.STOR_REQUEST_ERROR or data["packet_type"] == IR_PACKET_T.STOR_ERROR) :
            self.__errorDescription = data["errorDescription"]
            self.__image_not_found = True
        elif (data["packet_type"] == IR_PACKET_T.RETR_START) :
            try :
                ftpClient = FTPClient()
                ftpClient.connect(self.__ftpServerIP, data['FTPServerPort'], self.__ftpTimeout, data['username'], data['password'])
                ftpClient.retrieveFile(data['fileName'], self.__workingDirectory, data['serverDirectory']) 
                ftpClient.disconnect()
            except Exception:
                self.__errorDescription = ERROR_DESC_T.VMSRVR_FTP_RETR_TRANSFER_ERROR
        elif (data["packet_type"] == IR_PACKET_T.STOR_START) :
            try :
                ftpClient = FTPClient()
                ftpClient.connect(self.__ftpServerIP, data['FTPServerPort'], self.__ftpTimeout, data['username'], data['password'])
                ftpClient.storeFile(self.__sourceFilePath, self.__workingDirectory, data['serverDirectory'])
                ftpClient.disconnect()
            except Exception:
                self.__errorDescription = ERROR_DESC_T.VMSRVR_FTP_RETR_TRANSFER_ERROR
        elif (data["packet_type"] == IR_PACKET_T.ADDED_IMAGE_ID):
            self.__imageID = data["addedImageID"]                  
        self.__operation_completed = True   