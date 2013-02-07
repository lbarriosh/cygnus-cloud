# -*- coding: utf8 -*-
'''
Main server reactor definitions.
@author: Luis Barrios Hernández
@version: 1.0
'''

from callbacks import VMServerCallback, WebCallback
from database.utils.configuration import DBConfigurator
from database.mainServer.mainServerDB import MainServerDatabaseConnector, SERVER_STATE_T
from network.manager.networkManager import NetworkManager
from packets import MainServerPacketHandler, MAIN_SERVER_PACKET_T as WEB_PACKET_T
from virtualMachineServer.packets import VMServerPacketHandler, VM_SERVER_PACKET_T as VMSRVR_PACKET_T
from time import sleep
from loadBalancing.simpleLoadBalancer import SimpleLoadBalancer

class WebReactor(object):
    '''
    These objects react to packets received from a web server
    '''
    def processWebIncomingPacket(self, packet):
        raise NotImplementedError
    
class VMServerReactor(object):
    '''
    These objects react to packets received from a virtual machine server
    '''
    def processVMServerIncomingPacket(self, packet):
        raise NotImplementedError

class MainServerReactor(WebReactor, VMServerReactor):
    '''
    These objects react to packages received from the website or from
    a virtual machine server.
    '''
    def __init__(self):
        self.__webCallback = WebCallback(self)
        self.__finished = False
        
    def connectToDatabase(self, rootsPassword, dbName, dbUser, dbPassword, scriptPath):
        configurator = DBConfigurator(rootsPassword)
        configurator.runSQLScript(scriptPath)
        configurator.addUser(dbUser, dbPassword, dbName, True)
        self.__dbConnector = MainServerDatabaseConnector(dbUser, dbPassword, dbName)
        self.__dbConnector.connect()
        
    def startListenning(self, certificatePath, port):
        self.__loadBalancer = SimpleLoadBalancer(self.__dbConnector)
        self.__networkManager = NetworkManager(certificatePath)
        self.__webPort = port
        self.__networkManager.startNetworkService()        
        self.__webPacketHandler = MainServerPacketHandler(self.__networkManager)
        self.__vmServerPacketHandler = VMServerPacketHandler(self.__networkManager)
        self.__networkManager.listenIn(port, self.__webCallback, True)
        self.__vmServerCallback = VMServerCallback(self)
        
    def processWebIncomingPacket(self, packet):
        data = self.__webPacketHandler.readPacket(packet)
        if (data["packet_type"] == WEB_PACKET_T.REGISTER_VM_SERVER) :
            self.__registerVMServer(data)
        elif (data["packet_type"] == WEB_PACKET_T.QUERY_VM_SERVERS_STATUS) :
            self.__sendVMServerStatusData()
        elif (data["packet_type"] == WEB_PACKET_T.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
            self.__unregisterOrShutdownVMServer(data["ServerNameOrIPAddress"], data["Halt"], data["Shut_down"])
        elif (data["packet_type"] == WEB_PACKET_T.BOOTUP_VM_SERVER) :
            self.__bootUpVMServer(data["ServerNameOrIPAddress"])
        elif (data["packet_type"] == WEB_PACKET_T.QUERY_AVAILABLE_IMAGES) :
            self.__sendAvailableImagesData()
        elif (data["packet_type"] == WEB_PACKET_T.VM_BOOT_REQUEST):
            self.__bootUpVM(data["VMName"], data["UserID"])
                
                
    def __registerVMServer(self, data):
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
            
    def __unregisterOrShutdownVMServer(self, key, halt, shutdown):
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
        if (shutdown) :
            self.__dbConnector.updateVMServerStatus(serverId, SERVER_STATE_T.SHUT_DOWN)
            self.__dbConnector.deleteVMServerStatics(serverId)
        else :
            # Update the virtual machine server's state
            self.__dbConnector.unsubscribeVMServer(key)   
            
    def __updateVMServerStatus(self, data):
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
            self.__networkManager.sendPacket(serverData["ServerIP"], self.__webPort, p)
        
    def __sendVMServerStatusData(self):
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
            port = self.__dbConnector.getVMServerBasicData(serverID)["ServerPort"]
            self.__networkManager.sendPacket('', port, p)    
    
    def processVMServerIncomingPacket(self, packet):
        data = self.__vmServerPacketHandler.readPacket(packet)
        if (data["packet_type"] == VMSRVR_PACKET_T.SERVER_STATUS) :
            self.__updateVMServerStatus(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.DOMAIN_CONNECTION_DATA) :
            self.__sendVMConnectionData(data)
            
    def __sendVMConnectionData(self, data):
        p = self.__webPacketHandler.createVMConnectionDataPacket(data["UserID"], data["VNCServerIP"], 
                                                                 data["VNCServerPort"], data["VNCServerPassword"])
        self.__networkManager.sendPacket('', self.__webPort, p)        
    
    def hasFinished(self):
        return self.__finished
        
    
