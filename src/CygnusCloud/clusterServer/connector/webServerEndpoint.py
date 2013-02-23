# -*- coding: utf8 -*-
'''
Cluster server endpoint definitions
@author: Luis Barrios Hernández
@version: 3.0
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
    Callback class used in the cluster server endpoint.
    """
    def __init__(self, endpoint):
        """
        Initializes the callback's state
        Args:
            endpoint: the cluster server endpoint that will process the incoming packets.
        """
        self.__connector = endpoint
        
    def processPacket(self, packet):
        """
        Processes an incoming packet
        Args:
            packet: the packet to process
        Returns: 
            Nothing
        """
        self.__connector._processIncomingPacket(packet)
        
class _ClusterServerEndpointUpdateHandler(UpdateHandler):
    """
    These objects will send the update request packets to the cluster server
    periodically.
    """
    def __init__(self, endpoint):
        """
        Initializes the callback's state
        Args:
            endpoint: the cluster server endpoint that will send the update request packets.
        """
        self.__connector = endpoint
        
    def sendUpdateRequestPackets(self):
        """
        Sends an update request packet to the cluster server.
        Args:
            None
        Returns:
            Nothing
        """
        self.__connector._sendUpdateRequestPackets()

class WebServerEndpoint(object):  
    """
    These objects communicate a cluster server and the web server.
    """
    
    def __init__(self):
        self.__stopped = False
    
    def connectToDatabases(self, mysqlRootsPassword, statusDBName, commandsDBName, statusdbSQLFilePath, commandsDBSQLFilePath,
                           websiteUser, websiteUserPassword, endpointUser, endpointUserPassword):
        """
        Establishes a connection with the system status database.
        Args:
            mysqlRootsPassword: MySQL root's password
            statusDBName: the status database name
            statusdbSQLFilePath: the database schema definition SQL file path
            websiteUser: the website user's name. 
            websiteUserPassword: the website user's password
            endpointUser: the update user's name. This user will have ALL privileges on the status database.
            endpointUserPassword: the update user's password.
        """        
        # Create the status database
        self.__rootsPassword = mysqlRootsPassword
        self.__statusDatabaseName = statusDBName
        self.__commandsDatabaseName = commandsDBName
        configurator = DBConfigurator(mysqlRootsPassword)
        configurator.runSQLScript(statusDBName, statusdbSQLFilePath)
        configurator.runSQLScript(commandsDBName, commandsDBSQLFilePath)
        # Register the website and the endpoint users
        configurator.addUser(websiteUser, websiteUserPassword, statusDBName, False)
        configurator.addUser(endpointUser, endpointUserPassword, statusDBName, True)
        configurator.addUser(websiteUser, websiteUserPassword, commandsDBName, True)
        configurator.addUser(endpointUser, endpointUserPassword, commandsDBName, True)
        # Create the database connectors
        self.__commandsDBConnector = CommandsDatabaseConnector(endpointUser, endpointUserPassword, 
                                                               commandsDBName, 1) 
        self.__writer = SystemStatusDatabaseWriter(endpointUser, endpointUserPassword, statusDBName)
        # Connect to the database
        self.__writer.connect()
        self.__commandsDBConnector.connect()
        
    def connectToClusterServer(self, certificatePath, clusterServerIP, clusterServerListenningPort, statusDBUpdateInterval):
        """
        Establishes a connection with the cluster server.
        Args:
            certificatePath: the server.crt and server.key directory path.
            clusterServerIP: the cluster server's IPv4 address
            clusterServerListenningPort: the cluster server's listenning port.
            statusDBUpdateInterval: the status database update interval (in seconds)
        Returns:
            Nothing
        """
        self.__manager = NetworkManager(certificatePath)
        self.__manager.startNetworkService()
        callback = _ClusterServerEndpointCallback(self)
        # Connect to the main server
        self.__clusterServerIP = clusterServerIP
        self.__clusterServerPort = clusterServerListenningPort
        self.__manager.connectTo(clusterServerIP, clusterServerListenningPort, 5, callback, True)
        while (not self.__manager.isConnectionReady(clusterServerIP, clusterServerListenningPort)) :
            sleep(0.1)
        # Create the packet handler
        self.__pHandler = ClusterServerPacketHandler(self.__manager)
        # Create the update thread
        self.__updateRequestThread = StatusDatabaseUpdateThread(_ClusterServerEndpointUpdateHandler(self), statusDBUpdateInterval)
        # Start it
        self.__updateRequestThread.start()
        
    def disconnectFromClusterServer(self):
        """
        Closes the connection with the cluster server.
        Args:
            haltVMServers: if True, the virtual machine servers will be halted immediately. If false, they will be
            halted until all their virtual machines have been shut down.
        Returns:
            Nothing
        @attention: DO NOT call this method inside a network thread (i.e. inside the web callback). If you do so,
        your application will hang.
        """
        # Send a halt packet to the cluster server
        p = self.__pHandler.createHaltPacket(self.__haltVMServers)
        self.__manager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        # Stop the update request thread
        self.__updateRequestThread.stop()
        # Close the database connections
        self.__commandsDBConnector.disconnect()
        self.__writer.disconnect()
        # Stop the network service
        self.__manager.stopNetworkService()
        # Delete the status database
        dbConfigurator = DBConfigurator(self.__rootsPassword)
        dbConfigurator.dropDatabase(self.__statusDatabaseName)
        dbConfigurator.dropDatabase(self.__commandsDatabaseName)    
        
    def _processIncomingPacket(self, packet):
        """
        Processes an incoming package (sent from the cluster server).
        Args:
            packet: the packet to process
        Returns:
            Nothing
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
        # Command outputs => serialize and add them to the commands database
        else :
            if (data["packet_type"] == PACKET_T.VM_SERVER_BOOTUP_ERROR) :
                (outputType, outputContent) = CommandsHandler.createVMServerBootUpErrorOutput(
                    data["ServerNameOrIPAddress"], data["ErrorMessage"])
            elif (data["packet_type"] == PACKET_T.VM_SERVER_REGISTRATION_ERROR) :
                (outputType, outputContent) = CommandsHandler.createVMServerRegistrationErrorOutput(
                    data["VMServerIP"], data["VMServerPort"], data["VMServerName"], data["ErrorMessage"])
            elif (data["packet_type"] == PACKET_T.VM_BOOT_FAILURE) :
                (outputType, outputContent) = CommandsHandler.createVMBootFailureErrorOutput(
                    data["VMID"], data["ErrorMessage"])  
            elif (data["packet_type"] == PACKET_T.VM_CONNECTION_DATA) :
                (outputType, outputContent) = CommandsHandler.createVMConnectionDataOutput(
                    data["VNCServerIPAddress"], data["VNCServerPort"], data["VNCServerPassword"])
            l = data["CommandID"].split("|")
            commandID = (int(l[0]), float(l[1]))
            self.__commandsDBConnector.addCommandOutput(commandID, outputType, outputContent)
            
    def processCommands(self):
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
        Sends the update request packets to the cluster server.
        Args:
            None
        Returns:
            Nothing
        """
        if (self.__stopped) :
            return
        # Send some update request packets to the cluster server
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
    statusDBUpdateInterval = 10
    endpoint.connectToDatabases(mysqlRootsPassword, statusDBName, commandsDBName, statusdbSQLFilePath, commandsdbSQLFilePath,
                               websiteUser, websiteUserPassword, 
                                endpointUser, endpointUserPassword)
    endpoint.connectToClusterServer(certificatePath, clusterServerIP, clusterServerListenningPort, statusDBUpdateInterval)
    endpoint.processCommands()
    endpoint.disconnectFromClusterServer()