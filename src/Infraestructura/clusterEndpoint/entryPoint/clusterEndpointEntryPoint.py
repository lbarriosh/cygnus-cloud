# -*- coding: utf8 -*-
'''
Definiciones del endpoint de la web
@author: Luis Barrios Hernández
@version: 3.5
'''

from clusterEndpoint.threads.databaseUpdateThread import VMServerMonitoringThread
from clusterEndpoint.threads.commandMonitoringThread import CommandsMonitoringThread
from clusterServer.packetHandling.packetHandler import ClusterServerPacketHandler
from ccutils.databases.configuration import DBConfigurator
from clusterEndpoint.databases.clusterEndpointDB import ClusterEndpointDBConnector
from network.manager.networkManager import NetworkManager
from time import sleep
from clusterEndpoint.databases.commandsDatabaseConnector import CommandsDatabaseConnector
from network.exceptions.networkManager import NetworkManagerException
from clusterEndpoint.commands.commandsHandler import CommandsHandler
from clusterEndpoint.reactors.commandsProcessor import CommandsProcessor
from clusterEndpoint.reactors.packetReactor import ClusterEndpointPacketReactor
from clusterEndpoint.codes.spanishCodesTranslator import SpanishCodesTranslator

class ClusterEndpointEntryPoint(object):  
    """
    Estos objetos comunican un servidor de cluster con la web
    """    
    def __init__(self):
        """
        Inicializa el estado del endpoint
        Argumentos:
            Ninguno
        """
        self.__commandExecutionThread = None
        self.__updateRequestThread = None
        self.__codeTranslator = SpanishCodesTranslator()
        self.__commandsHandler = CommandsHandler(self.__codeTranslator)       
    
    def connectToDatabases(self, mysqlRootsPassword, endpointDBName, commandsDBName, endpointdbSQLFilePath, commandsDBSQLFilePath,
                           websiteUser, websiteUserPassword, endpointUser, endpointUserPassword, minCommandInterval):
        """
        Establece la conexión con la base de datos de estado y con la base de datos de comandos.
        Argumentos:
            mysqlRootsPassword: la contraseña de root de MySQL
            endpointDBName: el nombre de la base de datos de estado
            endpointdbSQLFilePath: la ruta del script que crea la base de datos de estado
            websiteUser: nombre de usuario que usará la web para manipular las bases de datos
            websiteUserPassword: contraseña del usuario de la web
            endpointUser: usuario que utilizará en eldpoint para manipular las bases de datos de estado. Será el único
            que puede escribir en la base de datos de estado.
            endpointUserPassword: contraseña del usuario del endpoint
        """        
        # Crear las bases de datos
        self.__rootsPassword = mysqlRootsPassword
        self.__statusDatabaseName = endpointDBName
        self.__commandsDatabaseName = commandsDBName
        configurator = DBConfigurator(mysqlRootsPassword)
        configurator.runSQLScript(endpointDBName, endpointdbSQLFilePath)
        configurator.runSQLScript(commandsDBName, commandsDBSQLFilePath)
        # Registrar en ellas los usuarios
        configurator.addUser(websiteUser, websiteUserPassword, endpointDBName, False)
        configurator.addUser(endpointUser, endpointUserPassword, endpointDBName, True)
        configurator.addUser(websiteUser, websiteUserPassword, commandsDBName, True)
        configurator.addUser(endpointUser, endpointUserPassword, commandsDBName, True)
        # Crear los conectores
        self.__commandsDBConnector = CommandsDatabaseConnector(endpointUser, endpointUserPassword, 
                                                               commandsDBName, minCommandInterval) 
        self.__endpointDBConnector = ClusterEndpointDBConnector(endpointUser, endpointUserPassword, endpointDBName)
        
    def connectToClusterServer(self, certificatePath, clusterServerIP, clusterServerListenningPort, statusDBUpdateInterval,
                               commandTimeout, commandTimeoutCheckInterval):
        """
        Establece la conexión con el servidor de cluster
        Argumentos:
            certificatePath: la ruta del directorio con los ficheros server.crt y server.key.
            clusterServerIP: la IP del servidor de cluster
            clusterServerListenningPort: el puerto en el que escucha el servidor de cluster
            statusDBUpdateInterval: el periodo de actualización de la base de datos (en segundos)
        Devuelve:
            Nada
        Lanza:
            EnpointException: se lanza cuando no se puede establecer una conexión con el servidor web
        """
        self.__networkManager = NetworkManager(certificatePath)
        self.__networkManager.startNetworkService()

        self.__clusterServerIP = clusterServerIP
        self.__clusterServerPort = clusterServerListenningPort
        self.__packetHandler = ClusterServerPacketHandler(self.__networkManager)     
        self.__commandsProcessor = CommandsProcessor(self.__commandsHandler, self.__packetHandler, self.__networkManager, 
                 self.__clusterServerIP, self.__clusterServerPort, self.__commandsDBConnector, self.__endpointDBConnector)
        packetReactor = ClusterEndpointPacketReactor(self.__codeTranslator, self.__commandsHandler, self.__packetHandler, self.__commandsProcessor,
                                                     self.__endpointDBConnector, self.__commandsDBConnector)
        try :
            self.__networkManager.connectTo(clusterServerIP, clusterServerListenningPort, 5, packetReactor, True)
            while (not self.__networkManager.isConnectionReady(clusterServerIP, clusterServerListenningPort)) :
                sleep(0.1)                   
            self.__updateRequestThread = VMServerMonitoringThread(self.__packetHandler, self.__networkManager, self.__commandsProcessor, 
                                                                  self.__clusterServerIP, self.__clusterServerPort, statusDBUpdateInterval)
            self.__updateRequestThread.start()            
            self.__commandExecutionThread = CommandsMonitoringThread(self.__commandsDBConnector, commandTimeout, self.__commandsHandler, commandTimeoutCheckInterval)
            self.__commandExecutionThread.start()
        except NetworkManagerException as e :
            raise Exception(e.message)
        
    def doEmergencyStop(self):
        self.__networkManager.stopNetworkService()
        if (self.__updateRequestThread != None):
            self.__updateRequestThread.stop()
        if (self.__commandExecutionThread != None):
            self.__commandExecutionThread.stop()        
        
    def disconnectFromClusterServer(self):
        """
        Cierra la conexión con el servidor de cluster y borra las bases de datos de estado
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        @attention: Este método debe llamarse desde el hilo principal para evitar cuelgues
        """
        # Apagar el servidor de cluster
        p = self.__packetHandler.createHaltPacket(self.__commandsProcessor.haltVMServers())
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Cluster server halt", 
                                                         errorMessage)
        # Dejar de actualizar las bases de datos
        self.__updateRequestThread.stop()
        
        # Dejar de monitorizar los comandos
        self.__commandExecutionThread.stop()
        
        # Cerrar las conexiones con las bases de datos
        self.closeNetworkConnections()
        
    def closeNetworkConnections(self):
        """
        Cierra las conexiones con las bases de datos
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        # Detener el servicio de red
        self.__networkManager.stopNetworkService()
        
    def processCommands(self):
        self.__commandsProcessor.processCommands()