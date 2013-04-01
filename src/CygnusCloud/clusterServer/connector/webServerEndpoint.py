# -*- coding: utf8 -*-
'''
Definiciones del endpoint de la web
@author: Luis Barrios Hernández
@version: 3.5
'''

from databaseUpdateThread import StatusDatabaseUpdateThread, UpdateHandler
from clusterServer.networking.packets import ClusterServerPacketHandler, MAIN_SERVER_PACKET_T as PACKET_T
from database.utils.configuration import DBConfigurator
from database.systemStatusDB.systemStatusDBWriter import SystemStatusDatabaseWriter
from network.manager.networkManager import NetworkManager, NetworkCallback
from time import sleep
from commandsHandler import CommandsHandler, COMMAND_TYPE
from database.commands.commandsDatabaseConnector import CommandsDatabaseConnector

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
        self.__connector = endpoint
        
    def processPacket(self, packet):
        """
        Procesa un paquete recibido
        Argumentos:
            packet: el paquete que hay que procesar
        Devuelve: 
            Nada
        """
        self.__connector._processIncomingPacket(packet)
        
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
        self.__connector = endpoint
        
    def sendUpdateRequestPackets(self):
        """
        Envía los paquetes de solicitud del estado al servidor de cluster
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        self.__connector._sendUpdateRequestPackets()

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
                           websiteUser, websiteUserPassword, endpointUser, endpointUserPassword):
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
                                                               commandsDBName, 1) 
        self.__writer = SystemStatusDatabaseWriter(endpointUser, endpointUserPassword, statusDBName)
        # Establecer las conexiones con MySQL
        self.__writer.connect()
        self.__commandsDBConnector.connect()
        
    def connectToClusterServer(self, certificatePath, clusterServerIP, clusterServerListenningPort, statusDBUpdateInterval):
        """
        Establece la conexión con el servidor de cluster
        Argumentos:
            certificatePath: la ruta del directorio con los ficheros server.crt y server.key.
            clusterServerIP: la IP del servidor de cluster
            clusterServerListenningPort: el puerto en el que escucha el servidor de cluster
            statusDBUpdateInterval: el periodo de actualización de la base de datos (en segundos)
        Devuelve:
            Nada
        """
        self.__manager = NetworkManager(certificatePath)
        self.__manager.startNetworkService()
        callback = _ClusterServerEndpointCallback(self)
        # Establecer la conexión
        self.__clusterServerIP = clusterServerIP
        self.__clusterServerPort = clusterServerListenningPort
        self.__manager.connectTo(clusterServerIP, clusterServerListenningPort, 5, callback, True)
        while (not self.__manager.isConnectionReady(clusterServerIP, clusterServerListenningPort)) :
            sleep(0.1)
        # Preparar la recepción de paquetes y la actualización automática de la base de datos de estado
        self.__pHandler = ClusterServerPacketHandler(self.__manager)
        
        self.__updateRequestThread = StatusDatabaseUpdateThread(_ClusterServerEndpointUpdateHandler(self), statusDBUpdateInterval)

        self.__updateRequestThread.start()
        
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
        p = self.__pHandler.createHaltPacket(self.__haltVMServers)
        self.__manager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        # Dejar de actualizar las bases de datos
        self.__updateRequestThread.stop()
        # Cerrar las conexiones con las bases de datos
        self.__commandsDBConnector.disconnect()
        self.__writer.disconnect()
        # Detener el servicio de red
        self.__manager.stopNetworkService()
        # Borrar las bases de datos de comandos y de estado
        dbConfigurator = DBConfigurator(self.__rootsPassword)
        dbConfigurator.dropDatabase(self.__statusDatabaseName)
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
        data = self.__pHandler.readPacket(packet)
        if (data["packet_type"] == PACKET_T.VM_SERVERS_STATUS_DATA) :
            self.__writer.processVMServerSegment(data["Segment"], data["SequenceSize"], data["Data"])
        elif (data["packet_type"] == PACKET_T.VM_DISTRIBUTION_DATA) :
            self.__writer.processVMDistributionSegment(data["Segment"], data["SequenceSize"], data["Data"])
        elif (data["packet_type"] == PACKET_T.ACTIVE_VM_DATA) :
            self.__writer.processActiveVMSegment(data["Segment"], data["SequenceSize"], data["VMServerIP"], data["Data"])
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
                        packet = self.__pHandler.createVMServerBootUpPacket(parsedArgs["VMServerNameOrIP"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.REGISTER_VM_SERVER) :
                        packet = self.__pHandler.createVMServerRegistrationPacket(parsedArgs["VMServerIP"], 
                            parsedArgs["VMServerPort"], parsedArgs["VMServerName"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
                        packet = self.__pHandler.createVMServerUnregistrationOrShutdownPacket(parsedArgs["VMServerNameOrIP"], 
                            parsedArgs["Halt"], parsedArgs["Unregister"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.VM_BOOT_REQUEST) :
                        packet = self.__pHandler.createVMBootRequestPacket(parsedArgs["VMID"], parsedArgs["UserID"], serializedCommandID)
                    self.__manager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, packet)
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
        p = self.__pHandler.createDataRequestPacket(PACKET_T.QUERY_VM_SERVERS_STATUS)
        self.__manager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)        
        p = self.__pHandler.createDataRequestPacket(PACKET_T.QUERY_VM_DISTRIBUTION)
        self.__manager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        p = self.__pHandler.createDataRequestPacket(PACKET_T.QUERY_ACTIVE_VM_DATA)
        self.__manager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        
if __name__ == "__main__" :
    endpoint = WebServerEndpoint()
    mysqlRootsPassword = ""
    statusDBName ="SystemStatusDB"
    commandsDBName = "CommandsDB"
    statusdbSQLFilePath = "../../database/SystemStatusDB.sql"
    commandsdbSQLFilePath = "../../database/CommandsDB.sql"
    websiteUser = "website"
    websiteUserPassword = "CygnusCloud"
    endpointUser = "connector_user"
    endpointUserPassword = "CygnusCloud"
    certificatePath = "/home/luis/Certificates"
    clusterServerIP = "127.0.0.1"
    clusterServerListenningPort = 9000
    statusDBUpdateInterval = 2
    endpoint.connectToDatabases(mysqlRootsPassword, statusDBName, commandsDBName, statusdbSQLFilePath, commandsdbSQLFilePath,
                               websiteUser, websiteUserPassword, 
                                endpointUser, endpointUserPassword)
    endpoint.connectToClusterServer(certificatePath, clusterServerIP, clusterServerListenningPort, statusDBUpdateInterval)
    endpoint.processCommands()
    endpoint.disconnectFromClusterServer()