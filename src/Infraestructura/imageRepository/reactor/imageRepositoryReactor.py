# -*- coding: utf8 -*-
'''
Created on Apr 21, 2013

@author: luis
'''

from network.manager.networkManager import NetworkManager
from imageRepository.database.imageRepositoryDB import ImageRepositoryDBConnector
from imageRepository.packetHandling.packets import ImageRepositoryPacketHandler, PACKET_T
from network.ftp.configurableFTPServer import ConfigurableFTPServer
from ccutils.dataStructures.multithreadingList import GenericThreadSafeList
from ccutils.dataStructures.multithreadingCounter import MultithreadingCounter
from time import sleep
from ccutils.processes.childProcessManager import ChildProcessManager
from errors.codes import ERROR_DESC_T
from imageRepository.callbacks.ftpServerCallback import FTPServerCallback
from imageRepository.callbacks.packetsCallback import CommandsCallback
from os import path, mkdir

class ImageRepositoryReactor(object):
    """
    Clase principal del repositorio de imágenes
    """    
    
    def __init__(self, workingDirectory):
        """
        Inicializa el estado del repositorio
        Argumentos:
            workingDirectory: el directorio en el que se almacenarán los ficheros
        """
        self.__workingDirectory = workingDirectory        
        self.__slotCounter = MultithreadingCounter()
        self.__retrieveQueue = GenericThreadSafeList()
        self.__storeQueue = GenericThreadSafeList() 
        self.__finish = False   
        self.__networkManager = None
        self.__ftpServer = None    
    
    def connectToDatabase(self, repositoryDBName, repositoryDBUser, repositoryDBPassword):
        """
        Establece la conexión con la base de datos.
        Argumentos:
            repositoryDBName: el nombre de la base de datos
            repositoryDBUser: el usuario a utilizar
            repositoryDBPassword: la contraseña a utilizar
        Devuelve:
            Nada
        """
        self.__dbConnector = ImageRepositoryDBConnector(repositoryDBUser, repositoryDBPassword, repositoryDBName)
    
    def startListenning(self, networkInterface, certificatesDirectory, commandsListenningPort, ftpListenningPort, maxConnections,
                        maxConnectionsPerIP, uploadBandwidthRatio, downloadBandwidthRatio, ftpUsername, ftpPasswordLength): 
        """
        Arranca el servidor FTP y comienza a atender las peticiones recibidas por la conexión de comandos.
        Argumentos:
            networkInterface: la interfaz de red por la que viajará el tráfico FTP
            certificatesDirectory: el directorio en el que se encuentran los ficheros server.crt y server.key
            commandsListenningPort: el puerto por el que se escucharán los comandos
            ftpListenningPort: el puerto en el que escuchará el servidor FTP
            maxConnections: máximo número de conexiones FTP que estarán activas al mismo tiempo
            maxConnectionsPerIP: máximo número de conexiones que puede haber entre el servidor FTP y un host.
            uploadBandwidthRatio: fracción del ancho de banda de subida que se usará para transportar tráfico FTP
            downloadBandwidthRatio: fracción del ancho de banda de bajada que se usará para transportar tráfico FTP.
            ftpUsername: el nombre de usuario FTP que se utilizará
            ftpPasswordLength: la longitud de la contraseña
        Devuelve:
            Nada
        @attention: El ancho de banda se determina automáticamente en función de la interfaz de red escogida.
        @attention: La contraseña se fija aleatoriamente en cada ejecución
        """
        try :
            self.__maxConnections = maxConnections      
            self.__commandsListenningPort = commandsListenningPort
            self.__FTPListenningPort = ftpListenningPort
            self.__networkManager = NetworkManager(certificatesDirectory)
            self.__repositoryPacketHandler = ImageRepositoryPacketHandler(self.__networkManager)        
            
            self.__commandsCallback = CommandsCallback(self.__networkManager, self.__repositoryPacketHandler, commandsListenningPort, self.__dbConnector,
                                                       self.__retrieveQueue, self.__storeQueue, self.__workingDirectory)        
            
            self.__networkManager.startNetworkService()
            self.__networkManager.listenIn(commandsListenningPort, self.__commandsCallback, True)
            
            dataCallback = FTPServerCallback(self.__slotCounter, self.__dbConnector)
            
            self.__ftpUsername = ftpUsername
            self.__ftpPassword = ChildProcessManager.runCommandInForeground("openssl rand -base64 {0}".format(ftpPasswordLength), Exception)        
            
            self.__ftpServer = ConfigurableFTPServer("Image repository FTP Server")
       
            self.__ftpServer.startListenning(networkInterface, ftpListenningPort, maxConnections, maxConnectionsPerIP, 
                                             dataCallback, downloadBandwidthRatio, uploadBandwidthRatio)
            self.__ftpServer.addUser(self.__ftpUsername, self.__ftpPassword, self.__workingDirectory, "eramw")      
        except Exception as e:
            print "Error: " + e.message
            self.__finish = True
        
    def stopListenning(self):
        """
        Para el repositorio
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        @attention: Para evitar cuelges, ¡¡¡no llamar a este método desde ningún hilo de la red!!!
        """
        if (self.__ftpServer != None) :
            try :
                self.__ftpServer.stopListenning()
            except Exception :
                pass
        if (self.__networkManager != None) :
            self.__networkManager.stopNetworkService()
    
    def initTransfers(self):
        """
        Inicia las transferencias de subida y bajada a medida que se liberan los slots.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        @attention: Este método sólo devolverá el control cuando el repositorio tenga que apagarse.
        """
        store = False
        while not (self.__finish or self.__commandsCallback.haltReceived()):
            if (self.__slotCounter.read() == self.__maxConnections) :
                # No hay slots => dormir
                sleep(0.1)
            else :
                # Los hay => atender subidas y bajadas de forma equitativa
                self.__slotCounter.decrement()
                
                # Seleccionar una cola. Si las dos tienen algo, iremos alternándolas
                # entre distintas ejecuciones del bucle
                if (self.__retrieveQueue.isEmpty() and self.__storeQueue.isEmpty()) :
                    sleep(0.1)
                    continue                
                if (not self.__retrieveQueue.isEmpty() and self.__storeQueue.isEmpty()) :
                    queue = self.__retrieveQueue
                    store = False
                elif (self.__retrieveQueue.isEmpty() and not self.__storeQueue.isEmpty()) :
                    queue = self.__storeQueue
                    store = True
                else :
                    if (store) :
                        queue = self.__retrieveQueue
                        store = False
                    else :
                        queue = self.__storeQueue
                        store = True
                
                # Sacar la petición de la cola
                                   
                (imageID, clientIP, clientPort) = queue.pop(0)
                    
                # Generar todo lo que el usuario necesita para conectarse
                imageData = self.__dbConnector.getImageData(imageID)
                if (imageData == None) :
                    if (store) :
                        packet_type = PACKET_T.STOR_ERROR
                    else :
                        packet_type = PACKET_T.RETR_ERROR
                    p = self.__repositoryPacketHandler.createErrorPacket(packet_type, ERROR_DESC_T.IR_IMAGE_DELETED)
                    self.__networkManager.sendPacket('', self.__commandsListenningPort, p, clientIP, clientPort)
                else :
                    compressedFilePath = imageData["compressedFilePath"]    
                    
                    if (not "undefined" in compressedFilePath) :                                
                        serverDirectory = path.relpath(path.dirname(compressedFilePath), self.__workingDirectory)
                        compressedFileName = path.basename(compressedFilePath)
                    else :
                        serverDirectory = str(imageID)
                        compressedFileName = ""
                        serverDirectoryPath = path.join(self.__workingDirectory, serverDirectory)
                        if (path.exists(serverDirectoryPath)) :
                            # Si el directorio ya existe, puede tener mierda => lo borramos y lo volvemos a crear
                            ChildProcessManager.runCommandInForeground("rm -rf " + serverDirectoryPath, Exception)
                        mkdir(serverDirectoryPath)                        
                    
                    if (store) :
                        packet_type = PACKET_T.STOR_START
                    else :
                        packet_type = PACKET_T.RETR_START
                                    
                    p = self.__repositoryPacketHandler.createTransferEnabledPacket(packet_type, imageID, self.__FTPListenningPort, 
                                    self.__ftpUsername, self.__ftpPassword, serverDirectory, compressedFileName)
                        
                    # Enviárselo
                    self.__networkManager.sendPacket('', self.__commandsListenningPort, p, clientIP, clientPort)