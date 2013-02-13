# -*- coding: utf8 -*-
'''
Main server connector definitions
@author: Luis Barrios Hernández
@version: 1.1
'''

from databaseUpdateThread import StatusDatabaseUpdateThread, UpdateHandler
from clusterServer.networking.packets import ClusterServerPacketHandler, MAIN_SERVER_PACKET_T as PACKET_T
from database.utils.configuration import DBConfigurator
from database.systemStatusDB.systemStatusDBReader import SystemStatusDatabaseReader
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
        
class GenericWebCallback(object):
    """
    This class defines the interface that the web server will implement to process events.
    """
    def handleVMServerBootUpError(self, vmServerNameOrIP, errorMessage) :
        """
        Handles a virtual machine server boot error.
        Args:
            vmServerNameOrIP: the virtual machine server's name or IP address.
            errorMessage: an error message
        Returns:
            Nothing
        """
        print 'VM Server bootup error ' + vmServerNameOrIP + " " + errorMessage
    def handleVMServerRegistrationError(self, vmServerNameOrIP, errorMessage) :
        """
        Handles a virtual machine server registration error.
        Args:
            vmServerNameOrIP: the virtual machine server's name or IP address.
            errorMessage: an error message
        Returns:
            Nothing
        """
        print 'VM Server registration error ' + vmServerNameOrIP + " " + errorMessage
    def handleVMBootFailure(self, vmID, userID, errorMessage) :
        """
        Handles a virtual machine boot error.
        Args:
            vmID: the virtual machine's unique identifier.
            userID: the user's unique identifier.
            errorMessage: an error message
        Returns:
            Nothing
        """
        print 'VM Boot failure ' + str(vmID) + " " + str(userID) + " " + errorMessage
    def handleVMConnectionData(self, userID, vncSrvrIP, vncSrvrPort, vncSrvrPassword) :
        """
        Handles a virtual machine's VNC connection data
        Args:
            userID: the user's unique identifier.
            vncSrvrIP: the VNC server's IP address
            vncSrvrPort: the VNC server's port
            vncSrvrPassword: the VNC server's password
        Returns:
            Nothing
        """
        print 'VM Connection data ' + str(userID) + " " + vncSrvrIP + " " + str(vncSrvrPort) + " " + vncSrvrPassword

class ClusterServerConnector(object):  
    """
    These objects communicate a cluster server and the web server.
    """  
    def __init__(self, callback):
        """
        Initializes the connector's state.
        Args:
            callback: a GenericWebCallback instance. This object will process the incoming packages.
        """
        self.__stopped = False
        self.__callback = callback
    
    def connectToDatabase(self, rootsPassword, databaseName, websiteUser, websiteUserPassword, updateUser, updateUserPassword):
        """
        Establishes a connection with the system status database.
        Args:
            rootsPassword: MySQL root's password
            databaseName: the status database name
            websiteUser: the website user's name. This user will just have SELECT privileges on the status database.
            websiteUserPassword: the website user's password
            updateUser: the update user's name. This user will have ALL privileges on the status database.
            updateUserPassword: the update user's password.
        """        
        # Create the status database
        self.__rootsPassword = rootsPassword
        self.__databaseName = databaseName
        configurator = DBConfigurator(rootsPassword)
        configurator.runSQLScript(databaseName, "../../database/SystemStatusDB.sql")
        # Register the website and the update users
        configurator.addUser(websiteUser, websiteUserPassword, databaseName, False)
        configurator.addUser(updateUser, updateUserPassword, databaseName, True)
        # Create the database connectors
        self.__reader = SystemStatusDatabaseReader(websiteUser, websiteUserPassword, databaseName)
        self.__writer = SystemStatusDatabaseWriter(updateUser, updateUserPassword, databaseName)
        # Connect to the database
        self.__reader.connect()
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
        self.__reader.disconnect()
        self.__writer.disconnect()
        # Stop the network service
        self.__manager.stopNetworkService()
        # Delete the status database
        dbConfigurator = DBConfigurator(self.__rootsPassword)
        dbConfigurator.dropDatabase(self.__databaseName)
        
    def getVMServersData(self):
        """
        Returns the virtual machine servers' data
        Args:
            None
        Returns:
            A list of dictionaries containing all the virtual machine servers' data.
        """
        return self.__reader.getVMServersData()
    
    def getVMDistributionData(self):
        """
        Returns the virtual machines' distribution data
        Args:
            None
        Returns:
            A list of dictionaries containing the virtual machines' distribution data 
        """
        return self.__reader.getVMDistributionData()
    
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
        
    def getActiveVMsData(self):
        """
        Returns the active virtual machines data
        Args:
            None
        Returns:
            A list of dictionaries containing all the active virtual machines' data.
        """
        return self.__reader.getActiveVMsData()
        
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
        
if __name__ == "__main__" :
    connector = ClusterServerConnector(GenericWebCallback())
    connector.connectToDatabase("","SystemStatusDB", "websiteUser", "cygnuscloud", "updateUser", "cygnuscloud")
    connector.connectToClusterServer("/home/luis/Certificates", "127.0.0.1", 9000, 5)
    sleep(10)
    print connector.getVMServersData()
    print connector.getVMDistributionData()
    print connector.getActiveVMsData()
    connector.bootUpVMServer("Server1")
    sleep(10)
    print connector.getVMServersData()
    print connector.getActiveVMsData()
    connector.bootUpVirtualMachine(1, 1)
    sleep(10)
    connector.shutdownVMServer("Server1", True)
    sleep(10)
    print connector.getVMServersData()
    connector.disconnectFromClusterServer(True)
    