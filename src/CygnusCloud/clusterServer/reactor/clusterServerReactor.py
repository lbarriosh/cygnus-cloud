# -*- coding: utf8 -*-
'''
Main server reactor definitions.
@author: Luis Barrios Hernández
@version: 2.0
'''

from clusterServer.networking.callbacks import VMServerCallback, WebCallback
from database.utils.configuration import DBConfigurator
from database.clusterServer.clusterServerDB import ClusterServerDatabaseConnector, SERVER_STATE_T
from network.manager.networkManager import NetworkManager
from clusterServer.networking.packets import ClusterServerPacketHandler, MAIN_SERVER_PACKET_T as WEB_PACKET_T
from virtualMachineServer.packets import VMServerPacketHandler, VM_SERVER_PACKET_T as VMSRVR_PACKET_T
from time import sleep
from clusterServer.loadBalancing.simpleLoadBalancer import SimpleLoadBalancer
from network.twistedInteraction.connection import RECONNECTION_T

class WebPacketReactor(object):
    '''
    These objects react to packets received from a web server
    '''
    def processWebIncomingPacket(self, packet):
        raise NotImplementedError
    
class VMServerPacketReactor(object):
    '''
    These objects react to packets received from a virtual machine server
    '''
    def processVMServerIncomingPacket(self, packet):
        raise NotImplementedError

class ClusterServerReactor(WebPacketReactor, VMServerPacketReactor):
    '''
    These objects react to packages received from the website or from
    a virtual machine server.
    '''
    def __init__(self):
        """
        Initializes the reactor's state.
        Args:
            None
        """
        self.__webCallback = WebCallback(self)
        self.__finished = False
        
    def connectToDatabase(self, mysqlRootsPassword, dbName, dbUser, dbPassword, scriptPath):
        """
        Establishes a connection with the cluster server database.
        Args:
            mysqlRootsPassword: MySQL root's password
            dbName: the cluster server database's name
            dbUser: the cluster server database's user name
            dbPassword: the cluster server database's user password
            scriptPath: the cluster server database's initialization script path
        """
        configurator = DBConfigurator(mysqlRootsPassword)
        configurator.runSQLScript(dbName, scriptPath)
        configurator.addUser(dbUser, dbPassword, dbName, True)
        self.__dbConnector = ClusterServerDatabaseConnector(dbUser, dbPassword, dbName)
        self.__dbConnector.connect()
        
    def startListenning(self, certificatePath, port):
        """
        Starts the network service and creates a server connection.
        Args:
            certificatePath: the server.crt and server.key files path
            port: the listenning port
        Returns:
            Nothing
        """
        self.__loadBalancer = SimpleLoadBalancer(self.__dbConnector)
        self.__networkManager = NetworkManager(certificatePath)
        self.__webPort = port
        self.__networkManager.startNetworkService()        
        self.__webPacketHandler = ClusterServerPacketHandler(self.__networkManager)
        self.__vmServerPacketHandler = VMServerPacketHandler(self.__networkManager)
        self.__networkManager.listenIn(port, self.__webCallback, True)
        self.__vmServerCallback = VMServerCallback(self)
        
    def processWebIncomingPacket(self, packet):
        """
        Processes a packet received from the web server.
        Args:
            packet: the packet to process
        Returns:
            Nothing
        """
        data = self.__webPacketHandler.readPacket(packet)
        if (data["packet_type"] == WEB_PACKET_T.REGISTER_VM_SERVER) :
            self.__registerVMServer(data)
        elif (data["packet_type"] == WEB_PACKET_T.QUERY_VM_SERVERS_STATUS) :
            self.__sendVMServerStatusData()
        elif (data["packet_type"] == WEB_PACKET_T.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
            self.__unregisterOrShutdownVMServer(data["ServerNameOrIPAddress"], data["Halt"], data["Unregister"])
        elif (data["packet_type"] == WEB_PACKET_T.BOOTUP_VM_SERVER) :
            self.__bootUpVMServer(data["ServerNameOrIPAddress"])
        elif (data["packet_type"] == WEB_PACKET_T.VM_BOOT_REQUEST):
            self.__bootUpVM(data["VMID"], data["UserID"])
        elif (data["packet_type"] == WEB_PACKET_T.HALT) :
            self.__halt(data["HaltVMServers"])
        elif (data["packet_type"] == WEB_PACKET_T.QUERY_VM_DISTRIBUTION) :
            self.__sendVMDistributionData()
        elif (data["packet_type"] == WEB_PACKET_T.QUERY_ACTIVE_VM_DATA) :
            self.__requestVNCConnectionData()
            
    def __requestVNCConnectionData(self):
        """
        Sends a VNC connection data request packet to all the active virtual machine servers
        Args:
            None
        Returns:
            Nothing
        """
        # Create a VNC connection data packet
        p = self.__vmServerPacketHandler.createVMServerDataRequestPacket(VMSRVR_PACKET_T.QUERY_ACTIVE_VM_DATA)
        # Fetch the active virtual machine server's IP addresses and ports
        connectionData = self.__dbConnector.getActiveVMServersConnectionData()
        for cd in connectionData :
            self.__networkManager.sendPacket(cd["ServerIP"], cd["ServerPort"], p)
            
    def __halt(self, haltVMServers):
        """
        Shuts down the cluster (including the virtual machine servers).
        Args:
            haltVMServers: if True, all the active virtual machines will be destroyed and the virtual machine
            servers will be shut down. If false, the virtual machine servers will wait until there are no
            active virtual machines, and then they'll be shut down.
        """
        self.__finished = True              
        vmServersConnectionData = self.__dbConnector.getActiveVMServersConnectionData()
        if (vmServersConnectionData != None) :
            for connectionData in vmServersConnectionData :
                self.__unregisterOrShutdownVMServer(connectionData['ServerIP'], haltVMServers, False)  
                
    def __registerVMServer(self, data):
        """
        Processes a virtual machine server registration packet.
        Args:
            data: the received virtual machine server registration packet.
        Returns:
            Nothing
        """
        try :
            # Check if the IP address is assigned to another virtual machine server
            server_id = self.__dbConnector.getVMServerID(data["VMServerIP"])
            if (server_id != None) :
                raise Exception("The IP address " + data["VMServerIP"] + " is assigned to another VM server")
            # Check if the name is assigned to another virtual machine server
            server_id = self.__dbConnector.getVMServerID(data["VMServerName"])
            if (server_id != None) :
                raise Exception("The name " + data["VMServerName"] + " is assigned to another VM server")
            # Establish a connection
            self.__networkManager.connectTo(data["VMServerIP"], data["VMServerPort"], 
                                                20, self.__vmServerCallback, True, True)
            # Register the server on the database
            self.__dbConnector.registerVMServer(data["VMServerName"], data["VMServerIP"], 
                                                    data["VMServerPort"])
            # Command the virtual machine server to tell us its state
            p = self.__vmServerPacketHandler.createVMServerDataRequestPacket(VMSRVR_PACKET_T.SERVER_STATUS_REQUEST)
            while not self.__networkManager.isConnectionReady(data["VMServerIP"], data["VMServerPort"]) :
                sleep(0.1)
            self.__networkManager.sendPacket(data["VMServerIP"], data["VMServerPort"], p)
        except Exception as e:                
            p = self.__webPacketHandler.createVMRegistrationErrorPacket(data["VMServerIP"], 
                                                                            data["VMServerPort"], 
                                                                            data["VMServerName"], str(e))        
            self.__networkManager.sendPacket('', self.__webPort, p)
            
    def __unregisterOrShutdownVMServer(self, key, halt, unregister):
        """
        Processes a virtual machine server unregistration or shutdown packet.
        Args:
            key: the virtual machine server's IPv4 address or its name.
            halt: if True, the virtual machine server will be shut down immediately. If false, it'll
            wait until all the virtual machines are shut down, and then it will finally be shut down.
            unregister: if True, the virtual machine server will be deleted from the cluster server's database. 
        """
        # Shut down the server (if necessary)
        serverId = self.__dbConnector.getVMServerID(key)
        serverData = self.__dbConnector.getVMServerBasicData(serverId)
        status = serverData["ServerStatus"]
        if (status == SERVER_STATE_T.READY or status == SERVER_STATE_T.BOOTING) :
            if not halt :
                p = self.__vmServerPacketHandler.createVMServerShutdownPacket()
            else :
                p = self.__vmServerPacketHandler.createVMServerHaltPacket()
            self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)
            # Close the network connection
            self.__networkManager.closeConnection(serverData["ServerIP"], serverData["ServerPort"])
        if (unregister) :
            self.__dbConnector.updateVMServerStatus(serverId, SERVER_STATE_T.SHUT_DOWN)
            self.__dbConnector.deleteVMServerStatics(serverId)
        else :
            # Update the virtual machine server's state
            self.__dbConnector.unsubscribeVMServer(key)   
            
    def __updateVMServerStatus(self, data):
        """
        Processes a virtual machine server's status packet.
        Args:
            data: the received packet
        Returns:
            Nothing
        """
        # Fetch the virtual machine server's ID
        serverID = None
        while (serverID == None) :
            serverID = self.__dbConnector.getVMServerID(data["VMServerIP"])
            if (serverID == None) :
                sleep(0.1)
        # Change its status
        self.__dbConnector.updateVMServerStatus(serverID, SERVER_STATE_T.READY)
        self.__dbConnector.setVMServerStatistics(serverID, data["ActiveDomains"])
        
    def __bootUpVMServer(self, serverNameOrIPAddress):
        """
        Processes a virtual machine server boot packet.
        Args:
            serverNameOrIPAddress: the virtual machine server's name or IPv4 address.
        Returns:
            Nothing
        """
        try :
            serverId = self.__dbConnector.getVMServerID(serverNameOrIPAddress)
            if (serverId == None) :
                raise Exception("The virtual machine server is not registered")
            serverData = self.__dbConnector.getVMServerBasicData(serverId)
            # Connect to the virtual machine server
            self.__networkManager.connectTo(serverData["ServerIP"], serverData["ServerPort"], 
                                                20, self.__vmServerCallback, True, True)
            while not self.__networkManager.isConnectionReady(serverData["ServerIP"], serverData["ServerPort"]) :
                sleep(0.1)
            # Change its status
            self.__dbConnector.updateVMServerStatus(serverId, SERVER_STATE_T.BOOTING)
            # Send the status request
            p = self.__vmServerPacketHandler.createVMServerDataRequestPacket(VMSRVR_PACKET_T.SERVER_STATUS_REQUEST)
            self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)
        except Exception as e:
            p = self.__webPacketHandler.createVMServerBootUpErrorPacket(serverNameOrIPAddress, str(e))
            self.__networkManager.sendPacket('', self.__webPort, p)
            
    def __sendVMServerStatusData(self):
        """
        Processes a virtual machine server data request packet.
        Args:
            None
        Returns:
            Nothing
        """
        self.__sendStatusData(self.__dbConnector.getVMServerBasicData, self.__webPacketHandler.createVMServerStatusPacket)
        
    def __sendVMDistributionData(self):
        """
        Processes a virtual machine distribution data packet
        Args:
            None
        Returns:
            Nothing
        """    
        self.__sendStatusData(self.__dbConnector.getHostedImages, self.__webPacketHandler.createVMDistributionPacket)
        
    def __sendStatusData(self, queryMethod, packetCreationMethod):
        """
        Processes a data request packet.
        Args:
            queryMethod: the method that extracts the data from the database
            packetCreationMethod: the method that creates the packet
        Returns:
            Nothing
        """        
        segmentSize = 5
        segmentCounter = 1
        outgoingData = []
        serverIDs = self.__dbConnector.getVMServerIDs()
        if (len(serverIDs) == 0) :
            segmentCounter = 0
        segmentNumber = (len(serverIDs) / segmentSize)
        if (len(serverIDs) % segmentSize != 0) :
            segmentNumber += 1
            sendLastSegment = True
        else :
            sendLastSegment = False
        for serverID in serverIDs :
            row = queryMethod(serverID)
            if (isinstance(row, dict)) :
                outgoingData.append(row)
            else :
                outgoingData += row
            if (len(outgoingData) >= segmentSize) :
                # Flush
                packet = packetCreationMethod(segmentCounter, segmentNumber, outgoingData)
                self.__networkManager.sendPacket('', self.__webPort, packet)
                outgoingData = []
                segmentCounter += 1
        # Send the last segment
        if (sendLastSegment) :
            packet = packetCreationMethod(segmentCounter, segmentNumber, outgoingData)
            self.__networkManager.sendPacket('', self.__webPort, packet)             
                   
    def __bootUpVM(self, vmID, userID):
        """
        Processes a virtual machine boot request packet.
        Args:
            vmName: the virtual machine's ID
            userID: the user's unique identifier
        Returns:
            Nothing
        """
        # Choose the virtual machine server that will host the image
        (serverID, errorMessage) = self.__loadBalancer.assignVMServer(vmID)
        if (errorMessage != None) :
            # Something went wrong => warn the user
            p = self.__webPacketHandler.createVMBootFailurePacket(vmID, userID, errorMessage)
            self.__networkManager.sendPacket('', self.__webPort, p)
        else :
            # Ask the virtual machine server to boot up the VM
            p = self.__vmServerPacketHandler.createVMBootPacket(vmID, userID)
            serverData = self.__dbConnector.getVMServerBasicData(serverID)
            self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)    
    
    def processVMServerIncomingPacket(self, packet):
        """
        Processes a packet sent from a virtual machine server.
        Args:
            packet: the packet to process
        Returns:
            Nothing
        """
        data = self.__vmServerPacketHandler.readPacket(packet)
        if (data["packet_type"] == VMSRVR_PACKET_T.SERVER_STATUS) :
            self.__updateVMServerStatus(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.DOMAIN_CONNECTION_DATA) :
            self.__sendVMConnectionData(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.ACTIVE_VM_DATA) :
            self.__sendVNCConnectionData(packet)
            
    def processServerReconnectionData(self, ipAddress, reconnection_status) :
        """
        Processes a reconnection status event
        Args:
            ipAddress: the connection's IPv4 address
            port: the connection's port
            reconnection_status: the reconnection process' status
        Returns:
            Nothing
        """
        if (reconnection_status == RECONNECTION_T.RECONNECTING) : 
            status = SERVER_STATE_T.RECONNECTING
        elif (reconnection_status == RECONNECTION_T.REESTABLISHED) :
            status = SERVER_STATE_T.READY
        else :
            status = SERVER_STATE_T.CONNECTION_TIMED_OUT
        
        serverID = self.__dbConnector.getVMServerID(ipAddress)
        self.__dbConnector.updateVMServerStatus(serverID, status)
            
    def __sendVNCConnectionData(self, packet):
        """
        Processes a VNC connection data packet
        Args:
            packet: the packet to process
        Returns:
            Nothing
        """
        p = self.__webPacketHandler.createActiveVMsDataPacket(packet)
        self.__networkManager.sendPacket('', self.__webPort, p)
            
    def __sendVMConnectionData(self, data):
        """
        Processes a virtual machine connection data packet.
        Args:
            data: the packet to process' data.
        Returns:
            Nothing
        """
        p = self.__webPacketHandler.createVMConnectionDataPacket(data["UserID"], data["VNCServerIP"], 
                                                                 data["VNCServerPort"], data["VNCServerPassword"])
        self.__networkManager.sendPacket('', self.__webPort, p)        
    
    def hasFinished(self):
        """
        Indicates if the cluster server has finished or not.
        """
        return self.__finished
    
    def shutdown(self):
        """
        Shuts down the cluster server.
        Args:
            None
        Returns:
            Nothing
        @attention: this method MUST NOT be called from a network thread. If you do so, the application will hang!
        """
        self.__networkManager.stopNetworkService()