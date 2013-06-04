# -*- coding: utf8 -*-
'''
Created on May 31, 2013

@author: luis
'''

from network.manager.networkManager import NetworkCallback
from imageRepository.database.image_status_t import IMAGE_STATUS_T
from imageRepository.packetHandling.packet_t import PACKET_T
from errors.codes import ERROR_DESC_T
from ccutils.processes.childProcessManager import ChildProcessManager
from os import path, statvfs

class CommandsCallback(NetworkCallback):
    """
    Clase para el callback que procesará los datos recibidos por la conexión de comandos.
    """    
    def __init__(self, packetCreator, pHandler, listenningPort, dbConnector, retrieveQueue, storeQueue, workingDirectory):
        """
        Inicializa el estado del callback
        Argumentos:
            packetCreator: objeto que se usará para enviar paquetes
            pHandler: objeto que se usará para crear y deserializar paquetes
            listenningPort: el puerto de escucha de la conexión de comandos
            dbConnector: conector con la base de datos
            retrieveQueue: cola de peticiones de descarga
            storeQueue: cola de peticiones de subida    
        """
        self.__networkManager = packetCreator
        self.__repositoryPacketHandler = pHandler
        self.__commandsListenningPort = listenningPort
        self.__dbConnector = dbConnector    
        self.__haltReceived = False
        self.__retrieveQueue = retrieveQueue
        self.__storeQueue = storeQueue
        self.__workingDirectory = workingDirectory
        
    def processPacket(self, packet):
        """
        Procesa un paquete
        Argumentos:
            packet: el paquete recibido
        Devuelve:
            Nada
        """
        data = self.__repositoryPacketHandler.readPacket(packet)
        if (data["packet_type"] == PACKET_T.HALT):
            self.__haltReceived = True
        elif (data["packet_type"] == PACKET_T.ADD_IMAGE):
            self.__addNewImage(data)
        elif (data["packet_type"] == PACKET_T.RETR_REQUEST):
            self.__handleRetrieveRequest(data)    
        elif (data["packet_type"] == PACKET_T.STOR_REQUEST):
            self.__handleStorRequest(data)
        elif (data["packet_type"] == PACKET_T.DELETE_REQUEST):
            self.__deleteImage(data)
        elif (data["packet_type"] == PACKET_T.STATUS_REQUEST):
            self.__sendStatusData(data)
        elif (data["packet_type"] == PACKET_T.CANCEL_EDITION):
            self.__cancelImageEdition(data)
            
    def __cancelImageEdition(self, data):
        self.__dbConnector.cancelImageEdition(data["ImageID"])
        p = self.__repositoryPacketHandler.createImageRequestReceivedPacket(PACKET_T.IMAGE_EDITION_CANCELLED)
        self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data["clientIP"], data["clientPort"])
            
    def __sendStatusData(self, data):
        diskStats = statvfs(self.__workingDirectory)
        freeDiskSpace = diskStats.f_bfree * diskStats.f_frsize / 1024
        totalDiskSpace = diskStats.f_bavail * diskStats.f_frsize / 1024
        p = self.__repositoryPacketHandler.createStatusDataPacket(freeDiskSpace, totalDiskSpace)
        self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
    
    def __addNewImage(self, data):
        """
        Añade una nueva imagen al repositorio
        Argumentos:
            data: el contenido del paquete recibido
        Devuelve:
            Nada
        """
        imageID = self.__dbConnector.addImage()
        p = self.__repositoryPacketHandler.createAddedImagePacket(imageID)        
        value = self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        if (value != None) :
            self.__dbConnector.deleteImage(imageID)
     
    def __handleRetrieveRequest(self, data):
        """
        Procesa una petición de descarga
        Argumentos:
            data: el contenido del paquete recibido
        Devuelve:
            Nada
        """   
        imageData = self.__dbConnector.getImageData(data["imageID"])
        # Chequear errores
        if (imageData == None) :
            p = self.__repositoryPacketHandler.createErrorPacket(PACKET_T.RETR_REQUEST_ERROR, ERROR_DESC_T.IR_UNKNOWN_IMAGE)
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        elif (imageData["imageStatus"] != IMAGE_STATUS_T.READY) :
            p = self.__repositoryPacketHandler.createErrorPacket(PACKET_T.RETR_REQUEST_ERROR, ERROR_DESC_T.IR_IMAGE_EDITED)
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        else:
            # No hay errores => contestar diciendo que hemos recibido la petición y encolarla
            p = self.__repositoryPacketHandler.createImageRequestReceivedPacket(PACKET_T.RETR_REQUEST_RECVD)
            value = self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
            if (value == None) :    
                self.__retrieveQueue.append((data["imageID"], data["clientIP"], data["clientPort"]))
                if (data["modify"]) :
                    self.__dbConnector.changeImageStatus(data["imageID"], IMAGE_STATUS_T.EDITION)
    
    def __handleStorRequest(self, data):
        """
        Procesa una petición de subida
        Argumentos:
            data: el contenido del paquete recibido
        Devuelve:
            Nada
        """   
        imageData = self.__dbConnector.getImageData(data["imageID"])
        # Chequear errores
        if (imageData == None) :
            p = self.__repositoryPacketHandler.createErrorPacket(PACKET_T.STOR_REQUEST_ERROR, ERROR_DESC_T.IR_UNKNOWN_IMAGE)
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        elif not (imageData["imageStatus"] == IMAGE_STATUS_T.EDITION or imageData["imageStatus"] == IMAGE_STATUS_T.NOT_RECEIVED) :
            p = self.__repositoryPacketHandler.createErrorPacket(PACKET_T.STOR_REQUEST_ERROR, ERROR_DESC_T.IR_NOT_EDITED_IMAGE)
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        else:
            # No hay errores => contestar diciendo que hemos recibido la petición y encolarla
            p = self.__repositoryPacketHandler.createImageRequestReceivedPacket(PACKET_T.STOR_REQUEST_RECVD)
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])            
            self.__storeQueue.append((data["imageID"], data["clientIP"], data["clientPort"]))        
            
    def __deleteImage(self, data):
        """
        Procesa una petición de borrado de una imagen
        Argumentos:
            data: el contenido del paquete recibido
        Devuelve:
            Nada
        """  
        imageData = self.__dbConnector.getImageData(data["imageID"])
        if (imageData == None) :
            p = self.__repositoryPacketHandler.createImageDeletionErrorPacket(data["imageID"], ERROR_DESC_T.IR_UNKNOWN_IMAGE)
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        elif (imageData["imageStatus"] == IMAGE_STATUS_T.EDITION):
            p = self.__repositoryPacketHandler.createImageDeletionErrorPacket(data["imageID"], ERROR_DESC_T.IR_EDITED_IMAGE)
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        else :            
            if (not "undefined" in imageData["compressedFilePath"]) :
                imageDirectory = path.dirname(imageData["compressedFilePath"])
                ChildProcessManager.runCommandInForeground("rm -rf " + imageDirectory, Exception)
            self.__dbConnector.deleteImage(data["imageID"]) # TODO: poner encima del if
            p = self.__repositoryPacketHandler.createDeleteRequestReceivedPacket(data["imageID"])
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])            
        
    def haltReceived(self):
        """
        Indica si se ha recibido un paquete de apagado o no
        Argumentos:
            Ninguno
        Devuelve:
            True si el repositorio debe apagarse, y false en caso contrario
        """   
        return self.__haltReceived