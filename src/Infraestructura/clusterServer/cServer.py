# -*- coding: utf8 -*-
'''
Definiciones del reactor del servidor de cluster
@author: Luis Barrios Hernández
@version: 4.0
'''
from time import sleep
from errors.codes import ERROR_DESC_T
from ccutils.databases.configuration import DBConfigurator
from network.manager.networkManager import NetworkManager
from networking.callbacks import VMServerCallback, WebCallback, ImageRepositoryCallback
from reactors.endpointPacketReactor import EndpointPacketReactor
from reactors.vmServerPacketReactor import VMServerPacketReactor
from reactors.imageRepositoryReactor import ImageRepositoryPacketReactor
from reactors.networkEventsReactor import NetworkEventsReactor
from networking.packets import ClusterServerPacketHandler, CLUSTER_SERVER_PACKET_T
from virtualMachineServer.networking.packets import VMServerPacketHandler
from imageRepository.packets import ImageRepositoryPacketHandler
from threads.clusterStatusMonitoringThread import ClusterStatusMonitoringThread
from database.clusterServerDB import ClusterServerDatabaseConnector, SERVER_STATE_T

class ClusterServer(object):
    '''
    Estos objetos reaccionan a los paquetes recibidos desde los servidores de máquinas
    virtuales y desde el endpoint de la web.
    '''
    def __init__(self, loadBalancerSettings, compressionRatio, dataImageExpectedSize, timeout):
        """
        Inicializa el estado del packetReactor
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """        
        self.__exit = False
        self.__loadBalancerSettings = loadBalancerSettings
        self.__compressionRatio = compressionRatio
        self.__dataImageExpectedSize = dataImageExpectedSize
        self.__timeout = timeout
        self.__statusMonitoringThread = None
        
    def connectToDatabase(self, mysqlRootsPassword, dbName, dbUser, dbPassword, scriptPath):
        """
        Establece la conexión con la base de datos del servidor de cluster.
        Argumentos:
            mysqlRootsPassword: La contraseña de root de MySQL
            dbName: nombre de la base de datos del servidor de cluster
            dbUser: usuario a utilizar
            dbPassword: contraseña del usuario a utilizar
            scriptPath: ruta del script de inicialización de la base de datos
        Devuelve:
            Nada
        """
        configurator = DBConfigurator(mysqlRootsPassword)
        configurator.runSQLScript(dbName, scriptPath)
        configurator.addUser(dbUser, dbPassword, dbName, True)
        self.__dbConnector = ClusterServerDatabaseConnector(dbUser, dbPassword, dbName)
        self.__dbConnector.resetVMServersStatus()
        
    def startListenning(self, certificatePath, listenningPort, repositoryIP, repositoryPort, vmServerStatusUpdateInterval):
        """
        Hace que el reactor comience a escuchar las peticiones del endpoint.
        Argumentos:
            certificatePath: ruta de los ficheros server.crt y server.key
            listenningPort: el puerto en el que se escuchará
        Devuelve:
            Nada
        """            
        # Preparamos todo lo necesario para conectarnos
        self.__networkManager = NetworkManager(certificatePath)        
        self.__networkManager.startNetworkService()    
        self.__listenningPort = listenningPort
        self.__webPacketHandler = ClusterServerPacketHandler(self.__networkManager)    
        imageRepositoryPacketHandler = ImageRepositoryPacketHandler(self.__networkManager)
        vmServerPacketHandler = VMServerPacketHandler(self.__networkManager)        
        networkEventsReactor = NetworkEventsReactor(self.__dbConnector, repositoryIP, repositoryPort)
        
        # Nos conectamos al repositorio               
        imageRepositoryPacketReactor = ImageRepositoryPacketReactor(self.__dbConnector, self.__networkManager,
                                                                    listenningPort, repositoryIP, repositoryPort,
                                                                    self.__webPacketHandler, vmServerPacketHandler, imageRepositoryPacketHandler)
        try :
            imageRepositoryCallback = ImageRepositoryCallback(imageRepositoryPacketReactor, networkEventsReactor)
            self.__networkManager.connectTo(repositoryIP, repositoryPort, 10, imageRepositoryCallback, True, True)
            self.__dbConnector.addImageRepository(repositoryIP, repositoryPort, SERVER_STATE_T.READY) 
        except Exception as e:
            print "Can't connect to the image repository: " + e.message
            self.__exit = True
            return        
        
        # Empezamos a escuchar las peticiones de la web
        
        vmServerPacketReactor = VMServerPacketReactor(self.__dbConnector, self.__networkManager, listenningPort,
                                                      vmServerPacketHandler, self.__webPacketHandler)
        
        self.__endpointPacketReactor = EndpointPacketReactor(self.__dbConnector, self.__networkManager, 
                                                             vmServerPacketHandler, self.__webPacketHandler,
                                                             imageRepositoryPacketHandler,
                                                             VMServerCallback(vmServerPacketReactor, networkEventsReactor),
                                                             listenningPort, repositoryIP, repositoryPort, self.__loadBalancerSettings,
                                                             self.__compressionRatio, self.__dataImageExpectedSize) 
        webCallback = WebCallback(self.__endpointPacketReactor)
        self.__networkManager.listenIn(listenningPort, webCallback, True)
       
        # Creamos el hilo que envía las actualizaciones de estado
        self.__statusMonitoringThread = ClusterStatusMonitoringThread(vmServerStatusUpdateInterval,
                                                                      self.__dbConnector, self.__networkManager,
                                                                      repositoryIP, repositoryPort,
                                                                      vmServerPacketHandler, imageRepositoryPacketHandler)
        self.__statusMonitoringThread.start()           
    
    def monitorVMBootCommands(self):
        """
        Elimina los comandos de arranque de máquinas virtuales que tardan demasiado tiempo en procesarse.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        
        while not self.__exit and not self.__endpointPacketReactor.hasFinished():
            data = self.__dbConnector.getOldVMBootCommandID(self.__timeout)
            if (data == None) :
                # Dormimos para no enviar demasiadas conexiones por segundo a MySQL
                sleep(1) 
            else :
                # Borramos la máquina activa (sabemos que no existe)
                self.__dbConnector.deleteActiveVMLocation(data[0])
                # Creamos el paquete de error y se lo enviamos al endpoint de la web
                p = self.__webPacketHandler.createErrorPacket(CLUSTER_SERVER_PACKET_T.VM_BOOT_FAILURE, ERROR_DESC_T.CLSRVR_VM_BOOT_TIMEOUT, data[0])
                self.__networkManager.sendPacket('', self.__listenningPort, p)
    
    def closeNetworkConnections(self):
        """
        Cierra todas las conexiones de red del servidor de máquinas virtuales.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        @attention: este método JAMÁS debe llamarse desde un hilo de red. 
        Si lo hacéis, la aplicación se colgará.
        """
        if (self.__statusMonitoringThread != None) :
            self.__statusMonitoringThread.stop()
        self.__networkManager.stopNetworkService()    