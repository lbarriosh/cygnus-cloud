# -*- coding: utf8 -*-
'''
Created on Apr 28, 2013

@author: luis
'''

from ccutils.threads.basicThread import BasicThread
from network.manager.networkManager import NetworkCallback
from network.ftp.ftpClient import FTPClient
from imageRepository.packetHandling.packetHandler import ImageRepositoryPacketHandler
from imageRepository.packetHandling.packet_t import PACKET_T as IR_PACKET_T
from virtualMachineServer.packetHandling.packet_t import VM_SERVER_PACKET_T
from time import sleep
from virtualMachineServer.database.transfer_t import TRANSFER_T
from errors.codes import ERROR_DESC_T
from ccutils.processes.childProcessManager import ChildProcessManager
from os import path

class FileTransferThread(BasicThread):
    """
    Clase del hilo de transferencias
    """
    def __init__(self, networkManager, serverListeningPort, packetHandler,
                 workingDirectory, ftpTimeout, dbConnector, max_cancel_timeout = 60):
        """
        Inicializa el estado del hilo de transferencias
        Argumentos:
            networkManager: gestor de red, que se usará para realizar las comunicaciones
            con el repositorio.
            serverListeningPort: el puerto en el que escucha el servidor de máquinas virtuales
            packetHandler: objeto que se usará para leer y crear paquetes
            workingDirectory: directorio en el que se colocarán los ficheros .zip que se intercambian
            con el repositorio de imágenes.
            ftpTimeout: el timeout máximo de las comunicaciones con el servidor FTP (en segundos)
        """
        BasicThread.__init__(self, "File transfer thread")
        self.__networkManager = networkManager
        self.__serverListeningPort = serverListeningPort
        self.__workingDirectory = workingDirectory
        self.__repositoryPacketHandler = ImageRepositoryPacketHandler(self.__networkManager)
        self.__vmServerPacketHandler = packetHandler
        self.__ftpTimeout = ftpTimeout
        self.__dbConnector = dbConnector
        self.__max_cancel_timeout = max_cancel_timeout
        
    def run(self):
        while not self.finish() :
            data = self.__dbConnector.peekFromTransferQueue()
            if data == None :
                sleep(0.5)
            else :
                self.__processElement(data)        
                self.__dbConnector.removeFirstElementFromTransferQueue()
        
    def __processElement(self, data):
        """
        Procesa una transferencia.
        Argumentos:
            data: un diccionario con los datos de la transferencia a procesar
        Devuelve:
            Nada
        """
        try :          
            # Generamos toda la información que necesitamos para iniciar la transferencia
            
            if (data["Transfer_Type"] == TRANSFER_T.CREATE_IMAGE or data["Transfer_Type"] == TRANSFER_T.EDIT_IMAGE) :
                p = self.__repositoryPacketHandler.createRetrieveRequestPacket(data["SourceImageID"], data["Transfer_Type"] == TRANSFER_T.EDIT_IMAGE)
                sourceFilePath = None
            elif (data["Transfer_Type"] == TRANSFER_T.DEPLOY_IMAGE):
                p = self.__repositoryPacketHandler.createRetrieveRequestPacket(data["SourceImageID"], False)
                sourceFilePath = None
            elif (data["Transfer_Type"] == TRANSFER_T.STORE_IMAGE):
                p = self.__repositoryPacketHandler.createStoreRequestPacket(int(data["TargetImageID"]))
                sourceFilePath = data["SourceFilePath"]
            else :
                p = self.__repositoryPacketHandler.createCancelEditionPacket(data["ImageID"])
                
            # Nos conectamos al repositorio
            callback = _FileTransferCallback(self.__repositoryPacketHandler, self.__workingDirectory, data["RepositoryIP"], self.__ftpTimeout,
                                             sourceFilePath)
            callback.prepareForNewTransfer()
            self.__networkManager.connectTo(data["RepositoryIP"], data["RepositoryPort"], 
                                            self.__ftpTimeout, callback)
            while not self.__networkManager.isConnectionReady(data["RepositoryIP"], data["RepositoryPort"]) :
                sleep(0.1)
                
            # Solicitamos el inicio de la transferencia
                
            self.__networkManager.sendPacket(data["RepositoryIP"], data["RepositoryPort"], p)
            
            
            if (data["Transfer_Type"] != TRANSFER_T.CANCEL_EDITION) :
                # Esperamos a que la transferencia termine
                while not callback.isTransferCompleted() :
                    sleep(0.1)
                timeout = False
            else :
                elapsed_time = 0
                while not callback.isTransferCompleted() and elapsed_time < self.__max_cancel_timeout:
                    sleep(0.1)
                    elapsed_time += 0.1
                timeout = elapsed_time >= self.__max_cancel_timeout
                
            if (callback.getErrorDescription() != None or timeout) :
                if (data["Transfer_Type"] != TRANSFER_T.CANCEL_EDITION):
                    # Error => informamos al usuario                
                    p = self.__vmServerPacketHandler.createErrorPacket(VM_SERVER_PACKET_T.IMAGE_EDITION_ERROR, 
                                                                       callback.getErrorDescription(), 
                                                                       data["CommandID"])
                else :
                    p = self.__vmServerPacketHandler.createInternalErrorPacket(data["CommandID"])
                    
                self.__networkManager.sendPacket('', self.__serverListeningPort, p)
            else :       
                # La transferencia ha acabado bien => determinamos qué hacer con el fichero que nos hemos descargado.
                
                if (data["Transfer_Type"] == TRANSFER_T.CREATE_IMAGE):
                    # Creamos una imagen nueva => debemos pedir un nuevo ID
                    callback.prepareForNewTransfer()
                    self.__networkManager.sendPacket(data["RepositoryIP"], data["RepositoryPort"], self.__repositoryPacketHandler.createAddImagePacket())
                    while not callback.isTransferCompleted() :
                        sleep(0.1)
                    data["TargetImageID"] = callback.getDomainImageID()
                    self.__dbConnector.addToCompressionQueue(data)
                elif (data["Transfer_Type"] == TRANSFER_T.EDIT_IMAGE or data["Transfer_Type"] == TRANSFER_T.DEPLOY_IMAGE):
                    # No tocaremos la imagen => nos limitamos a encolar la petición
                    data["TargetImageID"] = data["SourceImageID"]
                    self.__dbConnector.addToCompressionQueue(data)
                elif (data["Transfer_Type"] == TRANSFER_T.STORE_IMAGE) :
                    # Teníamos que subir la nueva imagen al repositorio => nos cargamos el fichero .zip y terminamos
                    ChildProcessManager.runCommandInForeground("rm " + path.join(self.__workingDirectory, data["SourceFilePath"]), Exception)
                    # Confirmamos que hemos subido la imagen
                    p = self.__vmServerPacketHandler.createImageEditedPacket(data["TargetImageID"], data["CommandID"])
                    self.__networkManager.sendPacket('', self.__serverListeningPort, p)
                
            # Nos desconectamos del repositorio
            self.__networkManager.closeConnection(data["RepositoryIP"], data["RepositoryPort"])

        except Exception:
            errorCode = ERROR_DESC_T.VMSRVR_IR_CONNECTION_ERROR
            try :
                self.__networkManager.closeConnection(data["RepositoryIP"], data["RepositoryPort"])
            except Exception:
                pass
            p = self.__vmServerPacketHandler.createErrorPacket(VM_SERVER_PACKET_T.IMAGE_EDITION_ERROR, 
                                                                errorCode, 
                                                                   data["CommandID"])
            self.__networkManager.sendPacket('', self.__serverListeningPort, p)
        
class _FileTransferCallback(NetworkCallback):
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