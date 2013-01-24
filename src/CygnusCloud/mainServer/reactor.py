# -*- coding: utf8 -*-
'''
Main server reactor definitions.
@author: Luis Barrios Hernández
@version: 1.0
'''

from callbacks import VMServerCallback, WebCallback
from database.utils.configuration import DBConfigurator
from database.mainServer.vmServerDB import VMServerDatabaseConnector, SERVER_STATE_T
from network.manager import NetworkManager
from network.exceptions.networkManager import NetworkManagerException
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
    def processVMServerIncomingPacket(self, packet, serverIP, port):
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
        configurator.runSQLScript()
        configurator.addUser(dbUser, dbPassword, databaseName, True)
        self.__dbConnector = VMServerDatabaseConnector(dbUser, dbPassword, databaseName)
        
    def startListenning(self, certificatePath, port):
        self.__networkManager = NetworkManager(certificatePath)
        self.__port = port
        self.__networkManager.startNetworkService()        
        self.__webPacketHandler = MainServerPacketHandler(self.__networkManager)
        self.__vmServerPacketHandler = VMServerPacketHandler(self.__networkManager)
        self.__networkManager.listenIn(port, self.__webCallback, True)
        
    def processWebIncomingPacket(self, packet):
        data = self.__webPacketHandler.readPacket(packet)
        if (data["packet_type"] == WEB_PACKET_T.REGISTER_VM_SERVER) :
           self.__registerVMServer(data)
                
                
    def __registerVMServer(self, data):
        try :
            # Establish a connection
            self.__networkManager.connectTo(data["VMServerIP"], data["VMServerPort"], 
                                                20, VMServerCallback(self, data["VMServerPort"]), True)
            # Register the server on the database
            self.__dbConnector.registerVMServer(data["VMServerName"], data["VMServerIP"], 
                                                    data["VMServerPort"])
            # Command the virtual machine server to tell us its state
            p = self.__vmServerPacketHandler.createVMServerStatusRequestPacket()
            self.__networkManager.sendPacket(data["VMServerPort"], p)
        except NetworkManagerException as e:                
            p = self.__webPacketHandler.createVMRegistrationErrorPacket(data["VMServerIP"], 
                                                                            data["VMServerPort"], 
                                                                            data["VMServerPort"], str(e))        
            self.__networkManager.sendPacket(self.__port, p)
            
    def __updateVMServerStatus(self, serverIP, port, data):
        # Fetch the virtual machine server's ID
        id = self.__dbConnector.getVMServerID(serverIP, port)
        # Change its status
        self.
        self.__dbConnector.updateVMServerStatus(id, SERVER_STATE_T.READY)
        
    
    def processVMServerIncomingPacket(self, packet, port):
        data = self.__vmServerPacketHandler.readPacket(packet)
        if (data["packet_type"] == VMSRVR_PACKET_T.SERVER_STATUS) :
            self.__updateVMServerStatus(port, data)
        
    
    def hasFinished(self):
        return self.__finished
        
    
