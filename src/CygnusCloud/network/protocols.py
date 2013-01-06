# -*- coding: utf8 -*-
'''
Protocol and protocol factory implementations.
@author: Luis Barrios Hernández
@version: 3.0
'''

from twisted.internet.protocol import Protocol, Factory
from network.packet import Packet

class _CygnusCloudProtocol(Protocol):
    """
    Network protocol implementation
    """
    def __init__(self, queue):
        """
        Initializes the protocol with an incoming data priority queue.
        Args:
            queue: The incoming data priority queue to use
        """
        self.__incomingPacketsQueue = queue
    
    def dataReceived(self, data):
        """
        Generates a packet with the received data and stores it on the
        incoming priority queue associated with the protocol instance.
        Args:
            data: The received data string
        Returns:
            Nothing
        Raises:
            PacketException: this exception will be raised when the received packet header
                is corrupt.
        """
        p = Packet._deserialize(data)
        self.__incomingPacketsQueue.queue(p.getPriority(), p)
    
    def connectionMade(self):
        """
        This method is called when a connection is established.
        """
        print "Connection established"
    
    def connectionLost(self, reason):
        """
        This method is called when a connection is lost
        Args:
            reason: a message indicating why the connection was lost.
        """
        print "Connection lost"  
    
    def sendData(self, packet):
        """
        Sends the a packet to its destination.
        Args:
            packet: The packet to send
        """
        self.transport.write(packet._serialize())
        
    def disconnect(self):
        """
        Closes a CLIENT connection.
        Args:
            None
        Returns:
            None
        """
        self.transport.loseConnection()
        
class _CygnusCloudProtocolFactory(Factory):
    """
    Protocol factory. These objects are used to create protocol instances
    within the Twisted Framework.
    """    
    def __init__(self, queue):
        """
        Initializes the protocol factory
        Args:
            queue: the incoming data queue to use by all protocol instances
        """
        self.protocol = _CygnusCloudProtocol
        self.__queue = queue        
        self.__instance = None    
    
    def buildProtocol(self, addr):
        """
        Builds a protocol, stores a pointer to it and finally returns it.
        This method is called inside Twisted code.
        """
        self.__instance = _CygnusCloudProtocol(self.__queue)        
        return self.__instance

    def getInstance(self):
        """
        Returns the last built instance
        Args:
            None
        Returns:
            the last built protocol instance
        """
        return self.__instance
    
    def getIncomingDataQueue(self):
        """
        Returns the incoming packages queue
        Args:
            None
        Returns:
            The incoming packages queue
        """
        return self.__queue
