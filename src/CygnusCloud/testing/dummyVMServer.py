# -*- coding: utf8 -*-
'''
In this module, we define a dummy virtual machine server.
This code will only be used for testing purposes.
@author: Luis Barrios Hernández
@version: 1.2
'''

from network.manager.networkManager import NetworkCallback, NetworkManager
from virtualMachineServer.packets import VMServerPacketHandler, VM_SERVER_PACKET_T as PACKET_T
from time import sleep

class DummyVMServer(NetworkCallback):
         
    """
    A class that behaves like a virtual machine server
    """
    
    def __init__(self, networkManager, dummyIP, port):
        """
        Initializes the callback's state
        """
        self.__packetHandler = VMServerPacketHandler(networkManager)
        self.__packetSender = lambda p : networkManager.sendPacket('', port, p)
        self.__dummyDomains = 0
        self.__dummyIP = dummyIP
        self.__finished = False
   
    def processPacket(self, packet):
        """
        Processes an incoming packet
        Args:
            packet: the incoming packet to process
        Returns:
            Nothing
        """
        # Process the packet
        processedPacket = self.__packetHandler.readPacket(packet)
        # Decide what to do with it
        packetType = processedPacket["packet_type"]
        if (packetType == PACKET_T.CREATE_DOMAIN) :
            self.__createDomain(processedPacket)            
        elif (packetType == PACKET_T.QUERY_ACTIVE_VM_DATA) :
            self.__sendActiveVMsData()
        elif (packetType == PACKET_T.HALT or packetType == PACKET_T.USER_FRIENDLY_SHUTDOWN) :
            print("The dummy virtual machine server is shutting down now")
            self.__finished = True
        else :
            # Server status request
            self.__sendStatusData()
            
    def hasFinished(self):
        """
        Returns a bool value indicating if the virtual machine server has been shut down
        or not.
        Args:
            None
        Returns:
            True if the virtual machine server has been shut down. Otherwise, False will be returned.
        """
        return self.__finished
            
    def __createDomain(self, processedPacket):
        """
        Creates a dummy domain and sends the connection data as an answer.
        """
        userID = processedPacket["UserID"]
        # Generate the answer
        packetToSend = self.__packetHandler.createVMConnectionParametersPacket(userID, self.__dummyIP, 
                                                                               12345, "dummy password")
        # Send it to the main server
        self.__packetSender(packetToSend)
        self.__dummyDomains += 1
        
    def __sendStatusData(self): 
        """
        Sends this server's status to the main server
        """
        # Generate the answer and send it
        packetToSend = self.__packetHandler.createVMServerStatusPacket(self.__dummyIP, self.__dummyDomains)
        self.__packetSender(packetToSend)
        
    def __sendActiveVMsData(self):
        statusData = [
            {"VMServerName" : "Server1", "UserID" : 1, "VMID" : 1, "VMName" : "Debian1", "VNCPort" : 15800, "VNCPass" : "Password" },
            {"VMServerName" : "Server1", "UserID" : 2, "VMID" : 1, "VMName" : "Debian1", "VNCPort" : 15802, "VNCPass" : "Password" }
            ]
        p = self.__packetHandler.createActiveVMsDataPacket(self.__dummyIP, 1, 1, statusData)
        self.__packetSender(p)
         
        
if __name__ == "__main__" :
    nmanager = NetworkManager("/home/luis/Certificates")
    nmanager.startNetworkService()
    print "Dummy virtual machine server - Version 1.0"
    ip = raw_input("IP address: ")
    port = int(raw_input("Port: "))
    callback = DummyVMServer(nmanager, ip, port)
    nmanager.listenIn(port, callback, True)
    while (not callback.hasFinished()) :
        sleep(1)
    nmanager.stopNetworkService()
    
            
    