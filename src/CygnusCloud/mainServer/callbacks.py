# -*- coding: utf8 -*-
'''
Main server callback definitions
@author: Luis Barrios Hernández
@version: 1.0
'''

from network.manager import NetworkCallback

class WebCallback(NetworkCallback):
    '''
    The web callback
    '''
    def __init__(self, reactor):
        self.__reactor = reactor
        
    def processPacket(self, packet):
        self.__reactor.processWebIncomingPacket(packet)
        
class VMServerCallback(NetworkCallback):
    '''
    The web callback
    '''
    def __init__(self, reactor, IPAddress, port):
        self.__reactor = reactor
        self.__IPAddress = IPAddress
        self.__port = port
        
    def processPacket(self, packet):
        self.__reactor.processVMServerIncomingPacket(packet, self.__IPAddress, self.__port)   
