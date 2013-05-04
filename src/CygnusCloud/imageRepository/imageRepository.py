# -*- coding: utf8 -*-
'''
Created on Apr 21, 2013

@author: luis
'''

from network.manager.networkManager import NetworkCallback, NetworkManager
from database.imageRepository.imageRepositoryDB import ImageRepositoryDBConnector, IMAGE_STATUS_T
from packets import ImageRepositoryPacketHandler, PACKET_T
from network.ftp.ftpServer import ConfigurableFTPServer, FTPCallback
from ccutils.dataStructures.multithreadingList import GenericThreadSafeList
from ccutils.dataStructures.multithreadingCounter import MultithreadingCounter
from os import remove, path, mkdir
from time import sleep
from ccutils.processes.childProcessManager import ChildProcessManager

class ImageRepository(object):
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
                                                       self.__retrieveQueue, self.__storeQueue)        
            
            self.__networkManager.startNetworkService()
            self.__networkManager.listenIn(commandsListenningPort, self.__commandsCallback, True)
            
            dataCallback = DataCallback(self.__slotCounter, self.__dbConnector)
            
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
        
        self.__dbConnector.disconnect()        
    
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
                    p = self.__repositoryPacketHandler.createErrorPacket(packet_type, "The image has been deleted")
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
                              
class CommandsCallback(NetworkCallback):
    """
    Clase para el callback que procesará los datos recibidos por la conexión de comandos.
    """    
    def __init__(self, packetCreator, pHandler, listenningPort, dbConnector, retrieveQueue, storeQueue):
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
        try :            
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        except Exception :
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
            p = self.__repositoryPacketHandler.createErrorPacket(PACKET_T.RETR_REQUEST_ERROR, "The image {0} does not exist".format(data["imageID"]))
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        elif (imageData["imageStatus"] != IMAGE_STATUS_T.READY) :
            p = self.__repositoryPacketHandler.createErrorPacket(PACKET_T.RETR_REQUEST_ERROR, "The image {0} is already being edited".format(data["imageID"]))
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        else:
            # No hay errores => contestar diciendo que hemos recibido la petición y encolarla
            p = self.__repositoryPacketHandler.createImageRequestReceivedPacket(PACKET_T.RETR_REQUEST_RECVD)
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])            
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
            p = self.__repositoryPacketHandler.createErrorPacket(PACKET_T.STOR_REQUEST_ERROR, "The image {0} does not exist".format(data["imageID"]))
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        elif not (imageData["imageStatus"] == IMAGE_STATUS_T.EDITION or imageData["imageStatus"] == IMAGE_STATUS_T.NOT_RECEIVED) :
            p = self.__repositoryPacketHandler.createErrorPacket(PACKET_T.STOR_REQUEST_ERROR, "The image {0} is not being edited".format(data["imageID"]))
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
            p = self.__repositoryPacketHandler.createErrorPacket(PACKET_T.DELETE_REQUEST_ERROR, "The image {0} does not exist".format(data["imageID"]))
            self.__networkManager.sendPacket('', self.__commandsListenningPort, p, data['clientIP'], data['clientPort'])
        else :            
            if (not "undefined" in imageData["compressedFilePath"]) :
                imageDirectory = path.dirname(imageData["compressedFilePath"])
                ChildProcessManager.runCommandInForeground("rm -rf " + imageDirectory, Exception)
            self.__dbConnector.deleteImage(data["imageID"]) # TODO: poner encima del if
            p = self.__repositoryPacketHandler.createImageRequestReceivedPacket(PACKET_T.DELETE_REQUEST_RECVD)
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
        
class DataCallback(FTPCallback):
    """
    Callback que procesará los eventos relacionados con las transferencias FTP
    """   
    def __init__(self, slotCounter, dbConnector):
        """
        Inicializa el estado del callback
        Argumentos:
            slotCounter: contador de slots
            dbConnector: conector con la base de datos
        """
        self.__slotCounter = slotCounter
        self.__dbConnector = dbConnector

    def on_disconnect(self):
        """
        Método que se invocará cuando un cliente se desconecta
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        self.__slotCounter.increment()

    def on_login(self, username):
        """
        Método que se invocará cuando un cliente inicia sesión
        Argumentos:
            username: el nombre del usuario
        Devuelve:
            nada
        """
        pass

    def on_logout(self, username):
        """
        Método que se invocará cuando un cliente cierra sesión
        Argumentos:
            username: el nombre del usuario
        Devuelve:
            Nada
        """
        pass

    def on_file_sent(self, f):
        """
        Método que se invocará cuando uun fichero acaba de transferirse
        Argumentos:
            f: el nombre del fichero
        Devuelve:
            Nada
        """
        pass
    
    def on_file_received(self, f):
        """
        Método que se invocará cuando un fichero acaba de recibirse
        Argumentos:
            f: el nombre del fichero
        Devuelve:
            Nada
        """
        self.__dbConnector.handleFinishedUploadTransfer(f)
    
    def on_incomplete_file_sent(self, f):
        """
        Método que se invocará cuando se interrumpe abruptamente la transferencia
        de un fichero
        Argumentos:
            f: el nombre del fichero
        Devuelve:
            Nada
        """
        pass

    def on_incomplete_f_received(self, f):    
        """
        Método que se invocará cuando se interrumpe abruptamente la subida
        de un fichero
        Argumentos:
            f: el nombre del fichero
        Devuelve:
            Nada
        """
        # Borramos el fichero y su directorio para no dejar mierda    
        remove(f)
        ChildProcessManager.runCommandInForeground("rm -rf " + path.dirname(f), Exception)