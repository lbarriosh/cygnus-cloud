# -*- coding: utf8 -*-
'''
Main server connector definitions
@author: Luis Barrios Hernández
@version: 1.0
'''

from databaseUpdateThread import StatusDatabaseUpdateThread, UpdateHandler
from mainServer.packets import MainServerPacketHandler, MAIN_SERVER_PACKET_T as PACKET_T
from database.utils.configuration import DBConfigurator
from database.systemStatusDB.systemStatusDBReader import SystemStatusDatabaseReader
from database.systemStatusDB.systemStatusDBWriter import SystemStatusDatabaseWriter
from network.manager import NetworkManager, NetworkCallback
from time import sleep

class _MainServerConnectorCallback(NetworkCallback):
    def __init__(self, connector):
        self.__connector = connector
        
    def processPacket(self, packet):
        self.__connector._processIncomingPacket(packet)
        
class _MainServerConnectorUpdateHandler(UpdateHandler):
    def __init__(self, connector):
        self.__connector = connector
        
    def sendUpdateRequestPackets(self):
        self.__connector._sendUpdateRequestPackets()
        
class GenericWebCallback(object):
    def handleVMServerBootUpError(self, vmServerNameOrIP, errorMessage) :
        print 'VM Server bootup error ' + vmServerNameOrIP + " " + errorMessage
    def handleVMServerRegistrationError(self, vmServerNameOrIP, errorMessage) :
        print 'VM Server registration error ' + vmServerNameOrIP + " " + errorMessage
    def handleVMBootFailure(self, vmName, userID, errorMessage) :
        print 'VM Boot failure ' + vmName + " " + userID + " " + errorMessage
    def handleVMConnectionData(self, userID, vncSrvrIP, vncSrvrPort, vncSrvrPassword) :
        print 'VM Connection data ' + userID + " " + vncSrvrIP + " " + vncSrvrPort + " " + vncSrvrPassword

class MainServerConnector(object):    

    def __init__(self, callback):
        self.__stopped = False
        self.__callback = callback
    
    def connectToDatabase(self, rootsPassword, websiteUser, websiteUserPassword, updateUser, updateUserPassword):
        # Create the status database
        configurator = DBConfigurator(rootsPassword)
        configurator.runSQLScript("../../database/SystemStatusDB.sql")
        # Register the website and the update users
        configurator.addUser(websiteUser, websiteUserPassword, "SystemStatusDB", False)
        configurator.addUser(updateUser, updateUserPassword, "SystemStatusDB", True)
        # Create the database connectors
        self.__reader = SystemStatusDatabaseReader(websiteUser, websiteUserPassword, "SystemStatusDB")
        self.__writer = SystemStatusDatabaseWriter(updateUser, updateUserPassword, "SystemStatusDB")
        # Connect to the database
        self.__reader.connect()
        self.__writer.connect()
        
    def connectToMainServer(self, certificatePath, mainServerIP, mainServerListenningPort):
        self.__manager = NetworkManager(certificatePath)
        callback = _MainServerConnectorCallback(self)
        # Connect to the main server
        self.__mainServerPort = mainServerListenningPort
        self.__manager.connectTo(mainServerIP, mainServerListenningPort, 5, callback, True)
        while (not self.__manager.isConnectionReady(mainServerListenningPort)) :
            sleep(0.1)
        # Create the packet handler
        self.__pHandler = MainServerPacketHandler(self.__manager)
        # Create the update thread
        self.__updateRequestThread = StatusDatabaseUpdateThread(_MainServerConnectorUpdateHandler(self), 20)
        # Start it
        self.__updateRequestThread.start()
        
    def disconnectFromMainServer(self):
        # Discard all the incoming packets and the scheduled updates
        self.__stopped = True
        # Stop the update request thread
        self.__updateRequestThread.stop()
        # Close the database connections
        self.__reader.disconnect()
        self.__writer.disconnect()
        # Stop the network service
        self.__manager.stopNetworkService()
        
    def getImages(self):
        return self.__reader.getImages()
        
    def getVMServersData(self):
        return self.__reader.getVMServersData()
    
    def registerVMServer(self, vmServerIP, vmServerPort, vmServerName):
        p = self.__pHandler.createVMServerRegistrationPacket(vmServerIP, vmServerPort, vmServerName)
        self.__manager.sendPacket(self.__mainServerPort, p)
        
    def unregisterVMServer(self, vmServerNameOrIP, halt):
        p = self.__pHandler.createVMServerUnregistrationOrShutdownPacket(vmServerNameOrIP, halt, False)
        self.__manager.sendPacket(self.__mainServerPort, p)
        
    def bootUpVMServer(self, vmServerNameOrIP):
        p = self.__pHandler.createVMServerBootUpPacket(vmServerNameOrIP)
        self.__manager.sendPacket(self.__mainServerPort, p)
        
    def shutdownVMServer(self, vmServerNameOrIP, halt):
        p = self.__pHandler.createVMServerUnregistrationOrShutdownPacket(vmServerNameOrIP, halt, True)
        self.__manager.sendPacket(self.__mainServerPort, p)
        
    def bootUpVirtualMachine(self, imageName, userID):
        p = self.__pHandler.createVMBootRequestPacket(imageName, userID)
        self.__manager.sendPacket(self.__mainServerPort, p)
        
    def _processIncomingPacket(self, packet):
        if (self.__stopped) :
            return
        data = self.__pHandler.readPacket(packet)
        if (data["packet_type"] == PACKET_T.VM_SERVERS_STATUS_DATA) :
            self.__writer.processVMServerSegment(data["Segment"], data["SequenceSize"], data["Data"])
        elif (data["packet_type"] == PACKET_T.AVAILABLE_IMAGES_DATA) :
            self.__writer.processImageSegment(data["Segment"], data["SequenceSize"], data["Data"])
        elif (data["packet_type"] == PACKET_T.VM_SERVER_BOOTUP_ERROR) :
            self.__callback.handleVMServerBootUpError(data["ServerNameOrIPAddress"], data["ErrorMessage"])
        elif (data["packet_type"] == PACKET_T.VM_SERVER_REGISTRATION_ERROR) :
            self.__callback.handleVMServerRegistrationError(data["ServerNameOrIPAddress"], data["ErrorMessage"])  
        elif (data["packet_type"] == PACKET_T.VM_BOOT_FAILURE) :
            self.__callback.handleVMBootFailure(data["VMName"], data["UserID"], data["ErrorMessage"])  
        elif (data["packet_type"] == PACKET_T.VM_CONNECTION_DATA) :
            self.__callback.handleVMConnectionData(data["UserID"], data["VNCServerIPAddress"], data["VNCServerPort"],
                                                   data["VNCServerPassword"])
    
    def _sendUpdateRequestPackets(self):
        if (self.__stopped) :
            return
        # Send some update request packets to the main server
        p = self.__pHandler.createDataRequestPacket(PACKET_T.QUERY_VM_SERVERS_STATUS)
        self.__manager.sendPacket(self.__mainServerPort, p)
        p = self.__pHandler.createDataRequestPacket(PACKET_T.QUERY_AVAILABLE_IMAGES)
        self.__manager.sendPacket(self.__mainServerPort, p)
        
if __name__ == "__main__" :
    connector = MainServerConnector(GenericWebCallback())
    connector.connectToDatabase("", "websiteUser", "cygnuscloud", "updateUser", "cygnuscloud")
    connector.connectToMainServer("/home/luis/Certificates", "127.0.0.1", 9000)
    sleep(10)
    print connector.getVMServersData()
    print connector.getImages()
    connector.disconnectFromMainServer()
    