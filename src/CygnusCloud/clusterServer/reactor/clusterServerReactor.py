# -*- coding: utf8 -*-
'''
Main server reactor definitions.
@author: Luis Barrios Hernández
@version: 1.1
'''

from clusterServer.networking.callbacks import VMServerCallback, WebCallback
from database.utils.configuration import DBConfigurator
from database.clusterServer.clusterServerDB import ClusterServerDatabaseConnector, SERVER_STATE_T
from network.manager.networkManager import NetworkManager
from clusterServer.networking.packets import MainServerPacketHandler, MAIN_SERVER_PACKET_T as WEB_PACKET_T
from virtualMachineServer.packets import VMServerPacketHandler, VM_SERVER_PACKET_T as VMSRVR_PACKET_T
from time import sleep
from clusterServer.loadBalancing.simpleLoadBalancer import SimpleLoadBalancer

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
        
    def connectToDatabase(self, rootsPassword, dbName, dbUser, dbPassword, scriptPath):
        """
        Establishes a connection with the cluster server database.
        Args:
            rootsPassword: MySQL root's password
            dbName: the cluster server database's name
            dbUser: the cluster server database's user name
            dbPassword: the cluster server database's user password
            scriptPath: the cluster server database's initialization script path
        """
        configurator = DBConfigurator(rootsPassword)
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
        self.__webPacketHandler = MainServerPacketHandler(self.__networkManager)
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
        elif (data["packet_type"] == WEB_PACKET_T.QUERY_AVAILABLE_IMAGES) :
            self.__sendAvailableImagesData()
        elif (data["packet_type"] == WEB_PACKET_T.VM_BOOT_REQUEST):
            self.__bootUpVM(data["VMName"], data["UserID"])
        elif (data["packet_type"] == WEB_PACKET_T.HALT) :
            self.__halt(data["HaltVMServers"])
            
    def __halt(self, haltVMServers):
        """
        Shuts down the cluster (including the virtual machine servers).
        Args:
            haltVMServers: if True, all the active virtual machines will be destroyed and the virtual machine
            servers will be shut down. If false, the virtual machine servers will wait until there are no
            active virtual machines, and then they'll be shut down.
        """
        # TODO: shut down all the virtual machine servers
        self.__finished = True                
                
    def __registerVMServer(self, data):
        """
        Processes a virtual machine server registration packet.
        Args:
            data: the received virtual machine server registration packet.
        Returns:
            Nothing
        """
        try :
            # Establish a connection
            self.__networkManager.connectTo(data["VMServerIP"], data["VMServerPort"], 
                                                20, self.__vmServerCallback, True)
            # Register the server on the database
            self.__dbConnector.subscribeVMServer(data["VMServerName"], data["VMServerIP"], 
                                                    data["VMServerPort"])
            # Command the virtual machine server to tell us its state
            p = self.__vmServerPacketHandler.createVMServerStatusRequestPacket()
            while not self.__networkManager.isConnectionReady(data["VMServerIP"], data["VMServerPort"]) :
                sleep(0.1)
            self.__networkManager.sendPacket(data["VMServerIP"], data["VMServerPort"], p)
        except Exception as e:                
            p = self.__webPacketHandler.createVMRegistrationErrorPacket(data["VMServerIP"], 
                                                                            data["VMServerPort"], 
                                                                            data["VMServerName"], str(e))        
            self.__networkManager.sendPacket(data["VMServerIP"], self.__webPort, p)
            
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
            serverData = self.__dbConnector.getVMServerBasicData(serverId)
            # Connect to the virtual machine server
            self.__networkManager.connectTo(serverData["ServerIP"], serverData["ServerPort"], 
                                                20, self.__vmServerCallback, True)
            while not self.__networkManager.isConnectionReady(serverData["ServerIP"], serverData["ServerPort"]) :
                sleep(0.1)
            # Change its status
            self.__dbConnector.updateVMServerStatus(serverId, SERVER_STATE_T.BOOTING)
            # Send the status request
            p = self.__vmServerPacketHandler.createVMServerStatusRequestPacket()
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
            row = self.__dbConnector.getVMServerBasicData(serverID)
            outgoingData.append(row)
            if (len(outgoingData) >= segmentSize) :
                # Flush
                packet = self.__webPacketHandler.createVMServerStatusPacket(segmentCounter, 
                                                                            segmentNumber, outgoingData)
                self.__networkManager.sendPacket('', self.__webPort, packet)
                outgoingData = []
                segmentCounter += 1
        # Send the last segment
        if (sendLastSegment) :
            packet = self.__webPacketHandler.createVMServerStatusPacket(segmentCounter, 
                                                                            segmentNumber, outgoingData)
            self.__networkManager.sendPacket('', self.__webPort, packet)             
        
    def __sendAvailableImagesData(self):
        """
        Processes an image data request packet.
        Args:
            None
        Returns:
            Nothing
        """
        segmentSize = 5
        segmentCounter = 1
        outgoingData = []
        imageIDs = self.__dbConnector.getImageIDs();
        if (len(imageIDs) == 0) :
            segmentCounter = 0  
        segmentNumber = (len(imageIDs) / segmentSize)
        if (len(imageIDs) % segmentSize != 0) :
            segmentNumber += 1  
            sendLastSegment = True
        else :
            sendLastSegment = False
        for imageID in imageIDs :
            row = self.__dbConnector.getImageData(imageID)
            outgoingData.append(row)
            if (len(outgoingData) >= segmentSize) :
                # Flush
                packet = self.__webPacketHandler.createAvailableImagesPacket(segmentCounter, 
                                                                            segmentNumber, outgoingData)
                self.__networkManager.sendPacket('', self.__webPort, packet)
                outgoingData = []
                segmentCounter += 1
        # Send the last segment
        if (sendLastSegment) :
            packet = self.__webPacketHandler.createAvailableImagesPacket(segmentCounter, 
                                                                            segmentNumber, outgoingData)
            self.__networkManager.sendPacket('', self.__webPort, packet) 
            
    def __bootUpVM(self, vmName, userID):
        """
        Processes a virtual machine boot request packet.
        Args:
            vmName: the virtual machine's name
            userID: the user's unique identifier
        Returns:
            Nothing
        """
        # Obtain the image's ID
        imageID = self.__dbConnector.getImageID(vmName)
        # Choose a virtual machine server to boot it
        (serverID, errorMessage) = self.__loadBalancer.assignVMServer(imageID)
        if (errorMessage != None) :
            # Something went wrong => warn the user
            p = self.__webPacketHandler.createVMBootFailurePacket(vmName, userID, errorMessage)
            self.__networkManager.sendPacket('', self.__webPort, p)
        else :
            # Ask the virtual machine server to boot up the VM
            p = self.__vmServerPacketHandler.createVMBootPacket(imageID, userID)
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