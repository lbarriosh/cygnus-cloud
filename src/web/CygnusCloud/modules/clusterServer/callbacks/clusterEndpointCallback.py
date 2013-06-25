'''
Created on Jun 2, 2013

@author: luis
'''
from network.manager.networkManager import NetworkCallback

class ClusterEndpointCallback(NetworkCallback):
    '''
    These callbacks will be used to process packets sent from the web server.
    '''
    def __init__(self, packetReactor):
        """
        Initializes the callback's state
        Args:
            packetReactor: the object that will process all the incoming packets
        """
        self.__packetReactor = packetReactor
        
    def processPacket(self, packet):
        """
        Processes an incoming packet sent from the web server.
        Args:
            packet:
                The packet to process
        Returns:
            Nothing
        """
        self.__packetReactor.processWebIncomingPacket(packet)