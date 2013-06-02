# -*- coding: utf8 -*-
'''
Main server callback definitions
@author: Luis Barrios Hernández
@version: 2.0
'''

from network.manager.networkManager import NetworkCallback
           
class ImageRepositoryCallback(NetworkCallback):
    '''
    These callbacks will be used to process packets sent from a virtual machine server.
    '''
    def __init__(self, packetReactor, networkEventsReactor):
        """
        Initializes the callback's state
        Args:
            packetReactor: the object that will process all the incoming packets
        """
        self.__packetReactor = packetReactor
        self.__networkEventsReactor = networkEventsReactor
        
    def processPacket(self, packet):
        """
        Processes an incoming packet sent from a virtual machine server.
        Args:
            packet:
                The packet to process
        Returns:
            Nothing
        """        
        self.__packetReactor.processImageRepositoryIncomingPacket(packet)   
        
    def processServerReconnectionData(self, ipAddress, port, reconnection_status):
        """
        Processes a reconnection status event
        Args:
            ipAddress: the connection's IPv4 address
            port: the connection's port
            reconnection_status: the reconnection process' status
        Returns:
            Nothing
        """
        self.__networkEventsReactor.processImageRepositoryReconnectionData(reconnection_status)