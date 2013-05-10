# -*- coding: utf8 -*-
'''
Definiciones del reactor del servidor de cluster
@author: Luis Barrios Hernández
@version: 4.0
'''
from clusterServer.networking.callbacks import VMServerCallback, WebCallback, ImageRepositoryCallback
from clusterServer.reactors.endpointPacketReactor import EndpointPacketReactor
from clusterServer.reactors.vmServerPacketReactor import VMServerPacketReactor
from clusterServer.reactors.imageRepositoryReactor import ImageRepositoryPacketReactor
from clusterServer.reactors.networkEventsReactor import NetworkEventsReactor


from clusterServer.threads.clusterStatusMonitoringThread import ClusterStatusMonitoringThread
from ccutils.databases.configuration import DBConfigurator
from clusterServer.database.clusterServerDB import ClusterServerDatabaseConnector, SERVER_STATE_T
from network.manager.networkManager import NetworkManager
from virtualMachineServer.networking.packets import VMServerPacketHandler
from time import sleep
from imageRepository.packets import ImageRepositoryPacketHandler
from errors.codes import ERROR_DESC_T
from clusterServer.networking.packets import ClusterServerPacketHandler


class ClusterServerReactor(object):
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
        self.__finished = False
        self.__loadBalancerSettings = loadBalancerSettings
        self.__compressionRatio = compressionRatio
        self.__dataImageExpectedSize = dataImageExpectedSize
        self.__timeout = timeout
        
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
        # Configurar las conexiones
        self.__networkManager = NetworkManager(certificatePath)
        self.__listenningPort = listenningPort
        self.__dbConnector.addImageRepository(repositoryIP, repositoryPort, SERVER_STATE_T.READY)
        self.__networkManager.startNetworkService()        
        self.__imageRepositoryPacketHandler = ImageRepositoryPacketHandler(self.__networkManager)
        self.__webPacketHandler = ClusterServerPacketHandler(self.__networkManager)
        self.__vmServerPacketHandler = VMServerPacketHandler(self.__networkManager)
        # Configurar los reactores
        vmServerPacketReactor = VMServerPacketReactor(self.__dbConnector, self.__networkManager, self.__listenningPort,
                                                      self.__vmServerPacketHandler, self.__webPacketHandler)
        imageRepositoryPacketReactor = ImageRepositoryPacketReactor(self.__dbConnector, self.__networkManager,
                                                                    self.__listenningPort, repositoryIP, repositoryPort,
                                                                    self.__webPacketHandler, self.__vmServerPacketHandler)
        networkEventsReactor = NetworkEventsReactor(self.__dbConnector)
        vmServerCallback = VMServerCallback(vmServerPacketReactor, networkEventsReactor)
        self.__endpointPacketReactor = EndpointPacketReactor(self.__dbConnector, self.__networkManager, 
                                                             self.__vmServerPacketHandler, self.__webPacketHandler,
                                                             self.__imageRepositoryPacketHandler, self.__listenningPort,
                                                             vmServerCallback,
                                                             repositoryIP, repositoryPort, self.__loadBalancerSettings) 
        
        self.__webCallback = WebCallback(self.__endpointPacketReactor)
        self.__imageRepositoryCallback = ImageRepositoryCallback(imageRepositoryPacketReactor, networkEventsReactor)
        
        try :
            self.__networkManager.connectTo(repositoryIP, repositoryPort, 10, self.__imageRepositoryCallback, True, True)
        except Exception as e:
            print "Can't connect to the image repository: " + e.message
            self.__finished = True
            return
            
        self.__networkManager.listenIn(listenningPort, self.__webCallback, True)        
        self.__vmServerStatusUpdateThread = ClusterStatusMonitoringThread(self, vmServerStatusUpdateInterval)
        self.__vmServerStatusUpdateThread.run()           
    
    def monitorVMBootCommands(self):
        """
        Elimina los comandos de arranque de máquinas virtuales que tardan demasiado tiempo en procesarse.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        while not self.__finished :
            data = self.__dbConnector.getOldVMBootCommandID(self.__timeout)
            if (not self.__finished and data == None) :
                # Dormimos para no enviar demasiadas conexiones por segundo a MySQL
                sleep(1) 
            else :
                # Borramos la máquina activa (sabemos que no existe)
                self.__dbConnector.deleteActiveVMLocation(data[0])
                # Creamos el paquete de error y se lo enviamos al endpoint de la web
                p = self.__webPacketHandler.createErrorPacket(ENDPOINT_PACKET_T.VM_BOOT_FAILURE, ERROR_DESC_T.CLSRVR_VM_BOOT_TIMEOUT, data[0])
                self.__networkManager.sendPacket('', self.__listenningPort, p)
    
    def hasFinished(self):
        """
        Indica al hilo principal si puede terminar o no.
        Argumentos:
            Ninguno
        Devuelve:
            True si se puede terminar, y false en caso contrario.
        """
        return self.__endpointPacketReactor.hasFinished()
    
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
        self.__networkManager.stopNetworkService()    