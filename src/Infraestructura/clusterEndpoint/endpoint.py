# -*- coding: utf8 -*-
'''
Definiciones del endpoint de la web
@author: Luis Barrios Hernández
@version: 3.5
'''

from clusterEndpoint.threads.databaseUpdateThread import VMServerMonitoringThread, UpdateHandler
from clusterEndpoint.threads.commandMonitoringThread import CommandsMonitoringThread
from clusterServer.networking.packets import ClusterServerPacketHandler, CLUSTER_SERVER_PACKET_T as PACKET_T
from ccutils.databases.configuration import DBConfigurator
from clusterEndpoint.databases.clusterEndpointDB import ClusterEndpointDBConnector
from network.manager.networkManager import NetworkManager, NetworkCallback
from time import sleep
from clusterEndpoint.commands.commandsHandler import CommandsHandler, COMMAND_TYPE, COMMAND_OUTPUT_TYPE
from clusterEndpoint.databases.commandsDatabaseConnector import CommandsDatabaseConnector
from network.exceptions.networkManager import NetworkManagerException
from endpointException import EndpointException

class _ClusterEndpointCallback(NetworkCallback):
    """
    Callback para procesar los paquetes enviados por el servidor de cluster
    """
    def __init__(self, endpoint):
        """
        Inicializa el estado del callback
        Argumentos:
            endpoint: el endpoint que procesará los paquetes entrantes
        """
        self.__endpoint = endpoint
        
    def processPacket(self, packet):
        """
        Procesa un paquete recibido
        Argumentos:
            packet: el paquete que hay que procesar
        Devuelve: 
            Nada
        """
        self.__endpoint._processIncomingPacket(packet)
        
class _ClusterEndpointUpdateHandler(UpdateHandler):
    """
    Estos objetos envían periódicamente paquetes al servidor de cluster para actualizar la base de datos de estado
    """
    def __init__(self, endpoint):
        """
        Inicializa el estado
        Argumentos:
            endpoint: el endpoint que enviará los paquetes
        """
        self.__endpoint = endpoint
        
    def sendUpdateRequestPackets(self):
        """
        Envía los paquetes de solicitud del estado al servidor de cluster
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        self.__endpoint._sendUpdateRequestPackets()

class ClusterEndpoint(object):  
    """
    Estos objetos comunican un servidor de cluster con la web
    """    
    def __init__(self, codeTranslator):
        """
        Inicializa el estado del endpoint
        Argumentos:
            Ninguno
        """
        self.__stopped = False
        self.__webPacketHandler = None
        self.__commandExecutionThread = None
        self.__updateRequestThread = None
        self.__codeTranslator = codeTranslator
        self.__commandsHandler = CommandsHandler(codeTranslator)
    
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
        callback = _ClusterEndpointCallback(self)
        # Establecer la conexión
        self.__clusterServerIP = clusterServerIP
        self.__clusterServerPort = clusterServerListenningPort
        try :
            self.__networkManager.connectTo(clusterServerIP, clusterServerListenningPort, 5, callback, True)
            while (not self.__networkManager.isConnectionReady(clusterServerIP, clusterServerListenningPort)) :
                sleep(0.1)
                    
            # TODO: si esto falla, terminar.
            # Preparar la recepción de paquetes y la actualización automática de la base de datos de estado
            self.__webPacketHandler = ClusterServerPacketHandler(self.__networkManager)
            
            self.__updateRequestThread = VMServerMonitoringThread(_ClusterEndpointUpdateHandler(self), statusDBUpdateInterval)
            self.__updateRequestThread.start()            
            self.__commandExecutionThread = CommandsMonitoringThread(self.__commandsDBConnector, commandTimeout, self.__commandsHandler, commandTimeoutCheckInterval)
            self.__commandExecutionThread.start()
        except NetworkManagerException as e :
            raise EndpointException(e.message)
        
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
        p = self.__webPacketHandler.createHaltPacket(self.__haltVMServers)
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Cluster server halt", 
                                                         errorMessage)
        # Dejar de actualizar las bases de datos
        self.__updateRequestThread.stop()
        
        # Dejar de monitorizar los comandos
        self.__commandExecutionThread.stop()
        
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
        self.__networkManager.stopNetworkService()
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
        data = self.__webPacketHandler.readPacket(packet)
        if (data["packet_type"] == PACKET_T.VM_SERVERS_STATUS_DATA) :
            processedData = self.__codeTranslator.processVMServerSegment(data["Data"])
            self.__endpointDBConnector.processVMServerSegment(data["Segment"], data["SequenceSize"], processedData)
        elif (data["packet_type"] == PACKET_T.VM_DISTRIBUTION_DATA) :
            processedData = self.__codeTranslator.processVMDistributionSegment(data["Data"])
            self.__endpointDBConnector.processVMDistributionSegment(data["Segment"], data["SequenceSize"], processedData)
        elif (data["packet_type"] == PACKET_T.REPOSITORY_STATUS):
            status = self.__codeTranslator.translateRepositoryStatusCode(data["RepositoryStatus"])
            self.__endpointDBConnector.updateImageRepositoryStatus(data["FreeDiskSpace"], data["AvailableDiskSpace"], status)
        elif (data["packet_type"] == PACKET_T.VM_SERVERS_RESOURCE_USAGE) :
            self.__endpointDBConnector.processVMServerResourceUsageSegment(data["Segment"], data["SequenceSize"], data["Data"])
        elif (data["packet_type"] == PACKET_T.ACTIVE_VM_DATA) :
            self.__endpointDBConnector.processActiveVMSegment(data["Segment"], data["SequenceSize"], data["VMServerIP"], data["Data"])
        else :
            l = data["CommandID"].split("|")
            commandID = (int(l[0]), float(l[1]))
            if (data["packet_type"] == PACKET_T.COMMAND_EXECUTED) :
                data = self.__commandsDBConnector.removeExecutedCommand(commandID)
                if (data["CommandType"] == COMMAND_TYPE.DEPLOY_IMAGE or data["CommandType"] == COMMAND_TYPE.DELETE_IMAGE or
                    data["CommandType"] == COMMAND_TYPE.CREATE_IMAGE or data["CommandType"] == COMMAND_TYPE.EDIT_IMAGE or
                    data["CommandType"] == COMMAND_TYPE.DELETE_IMAGE_FROM_INFRASTRUCTURE or data["CommandType"] == COMMAND_TYPE.AUTO_DEPLOY_IMAGE) :
                    # Crear notificación
                    self.__commandsDBConnector.addCommandOutput(commandID, COMMAND_OUTPUT_TYPE.IMAGE_DEPLOYED, 
                                                                self.__codeTranslator.translateNotificationCode(data["CommandType"]), 
                                                                False, True)
            else :           
                # El resto de paquetes contienen el resultado de ejecutar comandos => los serializamos y los añadimos
                # a la base de datos de comandos para que los conectores se enteren     
                isNotification = False     
                if (data["packet_type"] == PACKET_T.VM_CONNECTION_DATA) :
                    (outputType, outputContent) = self.__commandsHandler.createVMConnectionDataOutput(
                        data["VNCServerIPAddress"], data["VNCServerPort"], data["VNCServerPassword"]) 
                else :
                    # Errores
                    if (data["packet_type"] == PACKET_T.IMAGE_DEPLOYMENT_ERROR or data["packet_type"] == PACKET_T.DELETE_IMAGE_FROM_SERVER_ERROR or
                        data["packet_type"] == PACKET_T.IMAGE_CREATION_ERROR or data["packet_type"] == PACKET_T.IMAGE_EDITION_ERROR or
                        data["packet_type"] == PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR or data["packet_type"] == PACKET_T.AUTO_DEPLOY_ERROR):
                        isNotification = True
                    (outputType, outputContent) = self.__commandsHandler.createErrorOutput(data['packet_type'], data["ErrorDescription"])
                
                self.__commandsDBConnector.addCommandOutput(commandID, outputType, outputContent, False, isNotification)
                
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
                parsedArgs = self.__commandsHandler.deserializeCommandArgs(commandType, commandArgs)
                if (commandType != COMMAND_TYPE.HALT) :
                    serializedCommandID = "{0}|{1}".format(commandID[0], commandID[1])                    
                    if (commandType == COMMAND_TYPE.BOOTUP_VM_SERVER) :                    
                        packet = self.__webPacketHandler.createVMServerBootUpPacket(parsedArgs["VMServerNameOrIP"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.REGISTER_VM_SERVER) :
                        packet = self.__webPacketHandler.createVMServerRegistrationPacket(parsedArgs["VMServerIP"], 
                            parsedArgs["VMServerPort"], parsedArgs["VMServerName"], parsedArgs["IsVanillaServer"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
                        packet = self.__webPacketHandler.createVMServerUnregistrationOrShutdownPacket(parsedArgs["VMServerNameOrIP"], 
                            parsedArgs["Halt"], parsedArgs["Unregister"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.VM_BOOT_REQUEST) :
                        packet = self.__webPacketHandler.createVMBootRequestPacket(parsedArgs["VMID"], parsedArgs["UserID"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.DESTROY_DOMAIN):
                        packet = self.__webPacketHandler.createDomainDestructionPacket(parsedArgs["DomainID"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.VM_SERVER_CONFIGURATION_CHANGE) :
                        packet = self.__webPacketHandler.createVMServerConfigurationChangePacket(parsedArgs["VMServerNameOrIPAddress"],  parsedArgs["NewServerName"],
                                                                                         parsedArgs["NewServerIPAddress"], parsedArgs["NewServerPort"],
                                                                                         parsedArgs["NewVanillaImageEditionBehavior"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.DEPLOY_IMAGE):
                        packet = self.__webPacketHandler.createImageDeploymentPacket(PACKET_T.DEPLOY_IMAGE, parsedArgs["VMServerNameOrIPAddress"], 
                                                                                     parsedArgs["ImageID"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.DELETE_IMAGE):
                        packet = self.__webPacketHandler.createImageDeploymentPacket(PACKET_T.DELETE_IMAGE_FROM_SERVER, parsedArgs["VMServerNameOrIPAddress"], 
                                                                                     parsedArgs["ImageID"], serializedCommandID)     
                    elif (commandType == COMMAND_TYPE.CREATE_IMAGE):
                        packet = self.__webPacketHandler.createImageEditionPacket(PACKET_T.CREATE_IMAGE, parsedArgs["ImageID"], parsedArgs["OwnerID"], commandID) 
                    elif (commandType == COMMAND_TYPE.EDIT_IMAGE):   
                        packet = self.__webPacketHandler.createImageEditionPacket(PACKET_T.EDIT_IMAGE, parsedArgs["ImageID"], parsedArgs["OwnerID"], commandID)  
                    elif (commandType == COMMAND_TYPE.DELETE_IMAGE_FROM_INFRASTRUCTURE):
                        packet = self.__webPacketHandler.createImageDeletionPacket(parsedArgs["ImageID"], commandID)
                    elif (commandType == COMMAND_TYPE.AUTO_DEPLOY_IMAGE):
                        packet = self.__webPacketHandler.createAutoDeployPacket(parsedArgs["ImageID"], parsedArgs["MaxInstances"], commandID)
                                          
                    errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, packet)
                    if (errorMessage != None) :
                        # Error al enviar el paquete => el comando no se podrá ejecutar => avisar a la web
                        (outputType, outputContent) = self.__commandsHandler.createConnectionErrorOutput()
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
        p = self.__webPacketHandler.createDataRequestPacket(PACKET_T.QUERY_VM_SERVERS_STATUS)
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)          
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Virtual machine servers status", errorMessage)     
        
        p = self.__webPacketHandler.createDataRequestPacket(PACKET_T.QUERY_VM_DISTRIBUTION)
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)        
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Virtual machine distribution", errorMessage)
        
        p = self.__webPacketHandler.createDataRequestPacket(PACKET_T.QUERY_ACTIVE_VM_DATA)
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Active virtual machines data", errorMessage)
        
        p = self.__webPacketHandler.createDataRequestPacket(PACKET_T.QUERY_REPOSITORY_STATUS)
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Image repository status", errorMessage)
        
        p = self.__webPacketHandler.createDataRequestPacket(PACKET_T.QUERY_VM_SERVERS_RESOURCE_USAGE)
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Virtual machine servers resource usage", errorMessage)