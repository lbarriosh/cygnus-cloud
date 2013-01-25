# -*- coding: utf8 -*-
'''
Main server reactor definitions.
@author: Luis Barrios Hernández
@version: 1.0
'''

from callbacks import VMServerCallback, WebCallback
from database.utils.configuration import DBConfigurator
from database.mainServer.mainServerDB import MainServerDatabaseConnector, SERVER_STATE_T
from network.manager import NetworkManager
from packets import MainServerPacketHandler, MAIN_SERVER_PACKET_T as WEB_PACKET_T
from virtualMachineServer.packets import VMServerPacketHandler, VM_SERVER_PACKET_T as VMSRVR_PACKET_T

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
        
    def connectToDatabase(self, rootsPassword, dbUser, dbPassword, scriptPath, databaseName):
        configurator = DBConfigurator(rootsPassword)
        configurator.runSQLScript(scriptPath)
        configurator.addUser(dbUser, dbPassword, databaseName, True)
        self.__dbConnector = MainServerDatabaseConnector(dbUser, dbPassword, databaseName)
        self.__dbConnector.connect()
        
    def startListenning(self, certificatePath, port):
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
        if (data["packet_type"] == WEB_PACKET_T.QUERY_VM_SERVERS_STATUS) :
            self.__sendVMServerStatusData()
        if (data["packet_type"] == WEB_PACKET_T.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
            self.__unregisterOrShutdownVMServer(data["ServerNameOrIPAddress"], data["Halt"], data["Shut_down"])
        if (data["packet_type"] == WEB_PACKET_T.BOOOTUP_VM_SERVER) :
            self.__bootUpVMServer(data["ServerNameOrIPAddress"])
                
                
    def __registerVMServer(self, data):
        try :
            # Establish a connection
            self.__networkManager.connectTo(data["VMServerIP"], data["VMServerPort"], 
                                                20, self.__vmServerCallback, True)
            # Register the server on the database
            self.__dbConnector.registerVMServer(data["VMServerName"], data["VMServerIP"], 
                                                    data["VMServerPort"])
            # Command the virtual machine server to tell us its state
            p = self.__vmServerPacketHandler.createVMServerStatusRequestPacket()
            self.__networkManager.sendPacket(data["VMServerPort"], p)
        except Exception as e:                
            p = self.__webPacketHandler.createVMRegistrationErrorPacket(data["VMServerIP"], 
                                                                            data["VMServerPort"], 
                                                                            data["VMServerName"], str(e))        
            self.__networkManager.sendPacket(self.__webPort, p)
            
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
            self.__networkManager.sendPacket(serverData["ServerPort"], p)
        
        if (shutdown) :
            self.__dbConnector.updateVMServerStatus(serverId, SERVER_STATE_T.SHUT_DOWN)
        else :
            # Update the virtual machine server's state
            self.__dbConnector.unregisterVMServer(key)   
            
    def __updateVMServerStatus(self, data):
        # Fetch the virtual machine server's ID
        serverID = self.__dbConnector.getVMServerID(data["VMServerIP"])
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
            # Change its status
            self.__dbConnector.updateVMServerStatus(serverId, SERVER_STATE_T.BOOTING)
            # Send the status request
            p = self.__vmServerPacketHandler.createVMServerStatusRequestPacket()
            self.__networkManager.sendPacket(serverData["ServerPort"], p)
        except Exception as e:
            p = self.__webPacketHandler.createVMServerBootUpErrorPacket(serverNameOrIPAddress, str(e))
            self.__networkManager.sendPacket(self.__webPort, p)
        
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
        for serverID in serverIDs :
            row = self.__dbConnector.getVMServerBasicData(serverID)
            outgoingData.append(row)
            if (len(outgoingData) >= segmentSize) :
                # Flush
                packet = self.__webPacketHandler.createVMServerStatusPacket(segmentCounter, 
                                                                            segmentNumber, outgoingData)
                self.__networkManager.sendPacket(self.__webPort, packet)
                outgoingData = []
                segmentCounter += 1
        # Send the last segment
        packet = self.__webPacketHandler.createVMServerStatusPacket(segmentCounter, 
                                                                            segmentNumber, outgoingData)
        self.__networkManager.sendPacket(self.__webPort, packet)                
        
    
    def processVMServerIncomingPacket(self, packet):
        data = self.__vmServerPacketHandler.readPacket(packet)
        if (data["packet_type"] == VMSRVR_PACKET_T.SERVER_STATUS) :
            self.__updateVMServerStatus(data)
        
    
    def hasFinished(self):
        return self.__finished
        
    
