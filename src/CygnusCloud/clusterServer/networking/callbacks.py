# -*- coding: utf8 -*-
'''
Main server callback definitions
@author: Luis Barrios Hernández
@version: 1.0
'''

from network.manager.networkManager import NetworkCallback

class WebCallback(NetworkCallback):
    '''
    These callbacks will be used to process packets sent from the web server.
    '''
    def __init__(self, reactor):
        """
        Initializes the callback's state
        Args:
            reactor: the object that will process all the incoming packets
        """
        self.__reactor = reactor
        
    def processPacket(self, packet):
        """
        Processes an incoming packet sent from the web server.
        Args:
            packet:
                The packet to process
        Returns:
            Nothing
        """
        self.__reactor.processWebIncomingPacket(packet)
        
class VMServerCallback(NetworkCallback):
    '''
    These callbacks will be used to process packets sent from a virtual machine server.
    '''
    def __init__(self, reactor):
        """
        Initializes the callback's state
        Args:
            reactor: the object that will process all the incoming packets
        """
        self.__reactor = reactor
        
    def processPacket(self, packet):
        """
        Processes an incoming packet sent from a virtual machine server.
        Args:
            packet:
                The packet to process
        Returns:
            Nothing
        """        
        self.__reactor.processVMServerIncomingPacket(packet)   
