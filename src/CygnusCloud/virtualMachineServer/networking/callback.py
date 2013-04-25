# -*- coding: utf8 -*-

from network.manager.networkManager import NetworkCallback

class MainServerCallback(NetworkCallback):
    """
    Callback 
    """
    
    def __init__(self, processor):
        self.__processor = processor
        
    
    def processPacket(self, packet):
        self.__processor.processClusterServerIncomingPackets(packet)