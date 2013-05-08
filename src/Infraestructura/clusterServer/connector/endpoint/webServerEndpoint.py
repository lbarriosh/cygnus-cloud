# -*- coding: utf8 -*-
'''
Definiciones del endpoint de la web
@author: Luis Barrios Hernández
@version: 3.5
'''

from clusterServer.connector.threads.databaseUpdateThread import VMServerMonitoringThread, UpdateHandler
from clusterServer.connector.threads.commandMonitoringThread import CommandMonitoringThread
from clusterServer.networking.packets import ClusterServerPacketHandler, MAIN_SERVER_PACKET_T as PACKET_T
from database.utils.configuration import DBConfigurator
from database.clusterEndpoint.clusterEndpointDB import ClusterEndpointDBConnector
from network.manager.networkManager import NetworkManager, NetworkCallback
from time import sleep
from clusterServer.connector.commands.commandsHandler import CommandsHandler, COMMAND_TYPE
from database.commands.commandsDatabaseConnector import CommandsDatabaseConnector
from network.exceptions.networkManager import NetworkManagerException
from endpointException import EndpointException

class _ClusterServerEndpointCallback(NetworkCallback):
    """
    Callback para procesar los paquetes enviados por el servidor de cluster
    """
    def __init__(self, endpoint):
        """
        Inicializa el estado del callback
        Argumentos:
            endpoint: el endpoint que procesará los paquetes entrantes
        """
        self.__libvirtConnection = endpoint
        
    def processPacket(self, packet):
        """
        Procesa un paquete recibido
        Argumentos:
            packet: el paquete que hay que procesar
        Devuelve: 
            Nada
        """
        self.__libvirtConnection._processIncomingPacket(packet)
        
class _ClusterServerEndpointUpdateHandler(UpdateHandler):
    """
    Estos objetos envían periódicamente paquetes al servidor de cluster para actualizar la base de datos de estado
    """
    def __init__(self, endpoint):
        """
        Inicializa el estado
        Argumentos:
            endpoint: el endpoint que enviará los paquetes
        """
        self.__libvirtConnection = endpoint
        
    def sendUpdateRequestPackets(self):
        """
        Envía los paquetes de solicitud del estado al servidor de cluster
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        self.__libvirtConnection._sendUpdateRequestPackets()

class WebServerEndpoint(object):  
    """
    Estos objetos comunican un servidor de cluster con la web
    """    
    def __init__(self):
        """
        Inicializa el estado del endpoint
        Argumentos:
            Ninguno
        """
        self.__stopped = False
    
    def connectToDatabases(self, mysqlRootsPassword, statusDBName, commandsDBName, statusdbSQLFilePath, commandsDBSQLFilePath,
                           websiteUser, websiteUserPassword, endpointUser, endpointUserPassword, minCommandInterval):
        """
        Establece la conexión con la base de datos de estado y con la base de datos de comandos.
        Argumentos:
            mysqlRootsPassword: la contraseña de root de MySQL
            statusDBName: el nombre de la base de datos de estado
            statusdbSQLFilePath: la ruta del script que crea la base de datos de estado
            websiteUser: nombre de usuario que usará la web para manipular las bases de datos
            websiteUserPassword: contraseña del usuario de la web
            endpointUser: usuario que utilizará en eldpoint para manipular las bases de datos de estado. Será el único
            que puede escribir en la base de datos de estado.
            endpointUserPassword: contraseña del usuario del endpoint
        """        
        # Crear las bases de datos
        self.__rootsPassword = mysqlRootsPassword
        self.__statusDatabaseName = statusDBName
        self.__commandsDatabaseName = commandsDBName
        configurator = DBConfigurator(mysqlRootsPassword)
        configurator.runSQLScript(statusDBName, statusdbSQLFilePath)
        configurator.runSQLScript(commandsDBName, commandsDBSQLFilePath)
        # Registrar en ellas los usuarios
        configurator.addUser(websiteUser, websiteUserPassword, statusDBName, False)
        configurator.addUser(endpointUser, endpointUserPassword, statusDBName, True)
        configurator.addUser(websiteUser, websiteUserPassword, commandsDBName, True)
        configurator.addUser(endpointUser, endpointUserPassword, commandsDBName, True)
        # Crear los conectores
        self.__commandsDBConnector = CommandsDatabaseConnector(endpointUser, endpointUserPassword, 
                                                               commandsDBName, minCommandInterval) 
        self.__endpointDBConnector = ClusterEndpointDBConnector(endpointUser, endpointUserPassword, statusDBName)
        
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
        self.__manager = NetworkManager(certificatePath)
        self.__manager.startNetworkService()
        callback = _ClusterServerEndpointCallback(self)
        # Establecer la conexión
        self.__clusterServerIP = clusterServerIP
        self.__clusterServerPort = clusterServerListenningPort
        try :
            self.__manager.connectTo(clusterServerIP, clusterServerListenningPort, 5, callback, True)
            while (not self.__manager.isConnectionReady(clusterServerIP, clusterServerListenningPort)) :
                sleep(0.1)
                    
            # TODO: si esto falla, terminar.
            # Preparar la recepción de paquetes y la actualización automática de la base de datos de estado
            self.__repositoryPacketHandler = ClusterServerPacketHandler(self.__manager)
            
            self.__updateRequestThread = VMServerMonitoringThread(_ClusterServerEndpointUpdateHandler(self), statusDBUpdateInterval)
            self.__updateRequestThread.start()            
            self.__commandMonitoringThread = CommandMonitoringThread(self.__commandsDBConnector, commandTimeout, commandTimeoutCheckInterval)
            self.__commandMonitoringThread.start()
        except NetworkManagerException as e :
            raise EndpointException(e.message)
        
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
        p = self.__repositoryPacketHandler.createHaltPacket(self.__haltVMServers)
        errorMessage = self.__manager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Cluster server halt", 
                                                         errorMessage)
        # Dejar de actualizar las bases de datos
        self.__updateRequestThread.stop()
        
        # Dejar de monitorizar los comandos
        self.__commandMonitoringThread.stop()
        
        # Cerrar las conexiones con las bases de datos
        self.closeNetworkAndDBConnections()
        
    def closeNetworkAndDBConnections(self):
        """
        Cierra las conexiones con las bases de datos
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        # Detener el servicio de red
        self.__manager.stopNetworkService()
        # Borrar las bases de datos de comandos y de estado
        dbConfigurator = DBConfigurator(self.__rootsPassword)
        dbConfigurator.dropDatabase(self.__commandsDatabaseName)    
        
    def _processIncomingPacket(self, packet):
        """
        Procesa un paquete enviado desde el servidor de cluster
        Argumentos:
            packet: el paquete a procesar
        Devuelve:
            Nada
        """
        if (self.__stopped) :
            return
        data = self.__repositoryPacketHandler.readPacket(packet)
        if (data["packet_type"] == PACKET_T.VM_SERVERS_STATUS_DATA) :
            self.__endpointDBConnector.processVMServerSegment(data["Segment"], data["SequenceSize"], data["Data"])
        elif (data["packet_type"] == PACKET_T.VM_DISTRIBUTION_DATA) :
            self.__endpointDBConnector.processVMDistributionSegment(data["Segment"], data["SequenceSize"], data["Data"])
        elif (data["packet_type"] == PACKET_T.ACTIVE_VM_DATA) :
            self.__endpointDBConnector.processActiveVMSegment(data["Segment"], data["SequenceSize"], data["VMServerIP"], data["Data"])
        else :
            l = data["CommandID"].split("|")
            commandID = (int(l[0]), float(l[1]))
            if (data["packet_type"] == PACKET_T.COMMAND_EXECUTED) :
                self.__commandsDBConnector.removeExecutedCommand(commandID)
            else :           
                # El resto de paquetes contienen el resultado de ejecutar comandos => los serializamos y los añadimos
                # a la base de datos de comandos para que los conectores se enteren
                if (data["packet_type"] == PACKET_T.VM_SERVER_BOOTUP_ERROR or 
                    data["packet_type"] == PACKET_T.VM_SERVER_UNREGISTRATION_ERROR or 
                    data["packet_type"] == PACKET_T.VM_SERVER_SHUTDOWN_ERROR) :
                    (outputType, outputContent) = CommandsHandler.createVMServerGenericErrorOutput(
                        data["packet_type"], data["ServerNameOrIPAddress"], data["ErrorMessage"])
                elif (data["packet_type"] == PACKET_T.VM_SERVER_REGISTRATION_ERROR) :
                    (outputType, outputContent) = CommandsHandler.createVMServerRegistrationErrorOutput(
                        data["VMServerIP"], data["VMServerPort"], data["VMServerName"], data["ErrorMessage"])
                elif (data["packet_type"] == PACKET_T.VM_BOOT_FAILURE) :
                    (outputType, outputContent) = CommandsHandler.createVMBootFailureErrorOutput(
                        data["VMID"], data["ErrorMessage"])  
                elif (data["packet_type"] == PACKET_T.VM_CONNECTION_DATA) :
                    (outputType, outputContent) = CommandsHandler.createVMConnectionDataOutput(
                        data["VNCServerIPAddress"], data["VNCServerPort"], data["VNCServerPassword"])
                elif (data["packet_type"] == PACKET_T.DOMAIN_DESTRUCTION_ERROR):
                    (outputType, outputContent) = CommandsHandler.createDomainDestructionErrorOutput(data["ErrorMessage"])
                elif (data["packet_type"] == PACKET_T.VM_SERVER_CONFIGURATION_CHANGE_ERROR) :
                    (outputType, outputContent) = CommandsHandler.createVMServerConfigurationChangeErrorOutput(data["ErrorMessage"])
                self.__commandsDBConnector.addCommandOutput(commandID, outputType, outputContent)
                
    def processCommands(self):
        """
        Procesa los comandos enviados desde los conectores
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        while not self.__stopped :
            commandData = self.__commandsDBConnector.popCommand()
            if (commandData == None) :
                sleep(0.1)
            else :
                (commandID, commandType, commandArgs) = commandData
                parsedArgs = CommandsHandler.deserializeCommandArgs(commandType, commandArgs)
                if (commandType != COMMAND_TYPE.HALT) :
                    serializedCommandID = "{0}|{1}".format(commandID[0], commandID[1])                    
                    if (commandType == COMMAND_TYPE.BOOTUP_VM_SERVER) :                    
                        packet = self.__repositoryPacketHandler.createVMServerBootUpPacket(parsedArgs["VMServerNameOrIP"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.REGISTER_VM_SERVER) :
                        packet = self.__repositoryPacketHandler.createVMServerRegistrationPacket(parsedArgs["VMServerIP"], 
                            parsedArgs["VMServerPort"], parsedArgs["VMServerName"], parsedArgs["IsVanillaServer"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
                        packet = self.__repositoryPacketHandler.createVMServerUnregistrationOrShutdownPacket(parsedArgs["VMServerNameOrIP"], 
                            parsedArgs["Halt"], parsedArgs["Unregister"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.VM_BOOT_REQUEST) :
                        packet = self.__repositoryPacketHandler.createVMBootRequestPacket(parsedArgs["VMID"], parsedArgs["UserID"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.DESTROY_DOMAIN):
                        packet = self.__repositoryPacketHandler.createDomainDestructionPacket(parsedArgs["DomainID"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.VM_SERVER_CONFIGURATION_CHANGE) :
                        packet = self.__repositoryPacketHandler.createVMServerConfigurationChangePacket(parsedArgs["VMServerNameOrIPAddress"],  parsedArgs["NewServerName"],
                                                                                         parsedArgs["NewServerIPAddress"], parsedArgs["NewServerPort"],
                                                                                         parsedArgs["NewVanillaImageEditionBehavior"], serializedCommandID)
                    errorMessage = self.__manager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, packet)
                    if (errorMessage != None) :
                        # Error al enviar el paquete => el comando no se podrá ejecutar => avisar a la web
                        (outputType, outputContent) = CommandsHandler.createConnectionErrorOutput()
                        self.__commandsDBConnector.addCommandOutput(commandID, outputType, outputContent)
                        
                else :
                    self.__stopped = True
                    self.__haltVMServers = parsedArgs["HaltVMServers"]
    
    def _sendUpdateRequestPackets(self):
        """
        Solicita información de estado al serividor de cluster
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        if (self.__stopped) :
            return
        # Enviamos paquetes para obtener los tres tipos de información que necesitamos para actualizar la base de datos de estado
        p = self.__repositoryPacketHandler.createDataRequestPacket(PACKET_T.QUERY_VM_SERVERS_STATUS)
        errorMessage = self.__manager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)          
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Virtual machine servers status", errorMessage)     
        
        p = self.__repositoryPacketHandler.createDataRequestPacket(PACKET_T.QUERY_VM_DISTRIBUTION)
        errorMessage = self.__manager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)        
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Virtual machine distribution", errorMessage)
        
        p = self.__repositoryPacketHandler.createDataRequestPacket(PACKET_T.QUERY_ACTIVE_VM_DATA)
        errorMessage = self.__manager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Active virtual machines data", errorMessage)