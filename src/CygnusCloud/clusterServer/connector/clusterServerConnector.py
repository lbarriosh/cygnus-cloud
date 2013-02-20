# -*- coding: utf8 -*-
'''
Main server connector definitions
@author: Luis Barrios Hernández
@version: 1.1
'''

from databaseUpdateThread import StatusDatabaseUpdateThread, UpdateHandler
from clusterServer.networking.packets import ClusterServerPacketHandler, MAIN_SERVER_PACKET_T as PACKET_T
from database.utils.configuration import DBConfigurator
from database.systemStatusDB.systemStatusDBWriter import SystemStatusDatabaseWriter
from network.manager.networkManager import NetworkManager, NetworkCallback
from time import sleep

class _ClusterServerConnectorCallback(NetworkCallback):
    """
    Callback class used in the cluster server connector.
    """
    def __init__(self, connector):
        """
        Initializes the callback's state
        Args:
            connector: the cluster server connector that will process the incoming packets.
        """
        self.__connector = connector
        
    def processPacket(self, packet):
        """
        Processes an incoming packet
        Args:
            packet: the packet to process
        Returns: 
            Nothing
        """
        self.__connector._processIncomingPacket(packet)
        
class _ClusterServerConnectorUpdateHandler(UpdateHandler):
    """
    These objects will send the update request packets to the cluster server
    periodically.
    """
    def __init__(self, connector):
        """
        Initializes the callback's state
        Args:
            connector: the cluster server connector that will send the update request packets.
        """
        self.__connector = connector
        
    def sendUpdateRequestPackets(self):
        """
        Sends an update request packet to the cluster server.
        Args:
            None
        Returns:
            Nothing
        """
        self.__connector._sendUpdateRequestPackets()

class ClusterServerConnector(object):  
    """
    These objects communicate a cluster server and the web server.
    """  
    def __init__(self):
        """
        Initializes the connector's state.
        Args:
            callback: a GenericWebCallback instance. This object will process the incoming packages.
        """
        self.__stopped = False
    
    def connectToDatabase(self, mysqlRootsPassword, databaseName, sqlFilePath, websiteUser, websiteUserPassword, 
                          updateUser, updateUserPassword):
        """
        Establishes a connection with the system status database.
        Args:
            mysqlRootsPassword: MySQL root's password
            databaseName: the status database name
            sqlFilePath: the database schema definition SQL file path
            websiteUser: the website user's name. 
            websiteUserPassword: the website user's password
            updateUser: the update user's name. This user will have ALL privileges on the status database.
            updateUserPassword: the update user's password.
        """        
        # Create the status database
        self.__rootsPassword = mysqlRootsPassword
        self.__databaseName = databaseName
        configurator = DBConfigurator(mysqlRootsPassword)
        configurator.runSQLScript(databaseName, sqlFilePath)
        # Register the website and the update users
        configurator.addUser(websiteUser, websiteUserPassword, databaseName, False)
        configurator.addUser(updateUser, updateUserPassword, databaseName, True)
        # Create the database connectors
        self.__writer = SystemStatusDatabaseWriter(updateUser, updateUserPassword, databaseName)
        # Connect to the database
        self.__writer.connect()
        
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
        callback = _ClusterServerConnectorCallback(self)
        # Connect to the main server
        self.__clusterServerIP = clusterServerIP
        self.__clusterServerPort = clusterServerListenningPort
        self.__manager.connectTo(clusterServerIP, clusterServerListenningPort, 5, callback, True)
        while (not self.__manager.isConnectionReady(clusterServerIP, clusterServerListenningPort)) :
            sleep(0.1)
        # Create the packet handler
        self.__pHandler = ClusterServerPacketHandler(self.__manager)
        # Create the update thread
        self.__updateRequestThread = StatusDatabaseUpdateThread(_ClusterServerConnectorUpdateHandler(self), statusDBUpdateInterval)
        # Start it
        self.__updateRequestThread.start()
        
    def disconnectFromClusterServer(self, haltVMServers):
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
        p = self.__pHandler.createHaltPacket(haltVMServers)
        self.__manager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        # Discard all the incoming packets and the scheduled updates
        self.__stopped = True
        # Stop the update request thread
        self.__updateRequestThread.stop()
        # Close the database connections
        self.__writer.disconnect()
        # Stop the network service
        self.__manager.stopNetworkService()
        # Delete the status database
        dbConfigurator = DBConfigurator(self.__rootsPassword)
        dbConfigurator.dropDatabase(self.__databaseName)
    
    def registerVMServer(self, vmServerIP, vmServerPort, vmServerName):
        """
        Registers a virtual machine server in the cluster server.
        Args:
            vmServerIP: the virtual machine server's IPv4 address
            vmServerPort: the virtual machine server's listenning port
            vmServerName: the virtual machine server's name.
        Returns:
            Nothing
        """
        p = self.__pHandler.createVMServerRegistrationPacket(vmServerIP, vmServerPort, vmServerName)
        self.__manager.sendPacket(vmServerIP, self.__clusterServerPort, p)
        
    def unregisterVMServer(self, vmServerNameOrIP, halt):
        """
        Unregister a virtual machine server in the cluster server.
        Args:
            vmServerNameOrIP: the virtual machine server's name or IPv4 address
            halt: if True, the virtual machine server will destroy all the active virtual machines and terminate.
            If False, the virtual machine will wait for all the virtual machines to terminate, and then it will
            shut down.
        """
        p = self.__pHandler.createVMServerUnregistrationOrShutdownPacket(vmServerNameOrIP, halt, False)
        self.__manager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        
    def bootUpVMServer(self, vmServerNameOrIP):
        """
        Pairs a registered virtual machine server and the cluster server.
        Args:
            vmServerNameOrIP: the virtual machine server's name or IPv4 address.
        Returns:
            Nothing
        """
        p = self.__pHandler.createVMServerBootUpPacket(vmServerNameOrIP)
        self.__manager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        
    def shutdownVMServer(self, vmServerNameOrIP, halt):
        """
        Shuts down a virtual machine server
        Args:
            vmServerNameOrIP: the virtual machine server's name or IPv4 address
            halt: if True, the virtual machine server will destroy all the active virtual machines and terminate.
            If False, the virtual machine will wait for all the virtual machines to terminate, and then it will
            shut down.
        """
        p = self.__pHandler.createVMServerUnregistrationOrShutdownPacket(vmServerNameOrIP, halt, True)
        self.__manager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        
    def bootUpVirtualMachine(self, vmID, userID):
        """
        Boots up a virtual machine.
        Args:
            vmID: the virtual machine's unique identifier.
            userID: the user's unique identifier.
        Returns:
            Nothing
        """
        p = self.__pHandler.createVMBootRequestPacket(vmID, userID)
        self.__manager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        
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
        elif (data["packet_type"] == PACKET_T.VM_SERVER_BOOTUP_ERROR) :
            self.__callback.handleVMServerBootUpError(data["ServerNameOrIPAddress"], data["ErrorMessage"])
        elif (data["packet_type"] == PACKET_T.VM_SERVER_REGISTRATION_ERROR) :
            self.__callback.handleVMServerRegistrationError(data["ServerNameOrIPAddress"], data["ErrorMessage"])  
        elif (data["packet_type"] == PACKET_T.VM_BOOT_FAILURE) :
            self.__callback.handleVMBootFailure(data["VMID"], data["UserID"], data["ErrorMessage"])  
        elif (data["packet_type"] == PACKET_T.VM_CONNECTION_DATA) :
            self.__callback.handleVMConnectionData(data["UserID"], data["VNCServerIPAddress"], data["VNCServerPort"],
                                                   data["VNCServerPassword"])
    
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
        
    def has_finished(self):
        return self.__stopped
        
if __name__ == "__main__" :
    connector = ClusterServerConnector()
    mysqlRootsPassword = ""
    databaseName ="SystemStatusDB"
    sqlFilePath = "../../database/SystemStatusDB.sql"
    websiteUser = "website"
    websiteUserPassword = "CygnusCloud"
    updateUser = "connector_user"
    updateUserPassword = "CygnusCloud"
    certificatePath = "/home/luis/Certificates"
    clusterServerIP = "127.0.0.1"
    clusterServerListenningPort = 9000
    statusDBUpdateInterval = 10
    connector.connectToDatabase(mysqlRootsPassword, databaseName, sqlFilePath, websiteUser, websiteUserPassword, 
                                updateUser, updateUserPassword)
    connector.connectToClusterServer(certificatePath, clusterServerIP, clusterServerListenningPort, statusDBUpdateInterval)
    while not connector.has_finished() :
        sleep(1)