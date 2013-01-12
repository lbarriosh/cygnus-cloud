# -*- coding: utf8 -*-
'''
Protocol and protocol factory implementations.
@author: Luis Barrios Hernández
@version: 4.0
'''

from twisted.internet.protocol import Protocol, Factory
from network.packet import _Packet
from utils.multithreadingList import GenericThreadSafeList

class _CygnusCloudProtocol(Protocol):
    """
    Our custom network protocol.
    """
    def __init__(self, factory):
        """
        Initializes the protocol with the factory that created it.
        Args:
            factory: the protocol factory that created this protocol instance
        """       
        self.__factory = factory
        self.__disconnected = False
    
    def dataReceived(self, data):
        """
        Tells the protocol factory to process the received data.
        Args:
            data: The received data string
        Returns:
            Nothing
        Raises:
            PacketException: this exception will be raised when the received packet header
                is corrupt.
        """
        self.__factory.onPacketReceived(data)
    
    def connectionMade(self):
        """
        This method is called when a connection is established.
        Args:
            None
        Returns:
            Nothing
        """
        pass
    
    def connectionLost(self, reason):
        """
        This method is called when a connection is lost
        Args:
            reason: a message indicating why the connection was lost.
        Returns:
            Nothing
        """
        self.__disconnected = True
        self.__factory.removeConnection(self)
    
    def sendPacket(self, packet):
        """
        Sends the a packet to its destination.
        Args:
            packet: The packet to send
        Returns:
            Nothing
        """
        if (not self.__disconnected) :
            self.transport.write(packet._serialize())
        
    def disconnect(self):
        """
        Closes a CLIENT connection.
        Args:
            None
        Returns:
            Nothing
        """
        self.__disconnected = True
        self.transport.loseConnection()
        
class _CygnusCloudProtocolFactory(Factory):
    """
    Protocol factory. These objects are used to create protocol instances
    within the Twisted Framework, and store all the data shared by multiple
    protocol instances.
    """    
    def __init__(self, queue):
        """
        Initializes the protocol factory
        Args:
            queue: the incoming data queue to use by all protocol instances
        """
        self.protocol = _CygnusCloudProtocol
        self.__queue = queue        
        self.__connections = GenericThreadSafeList()
    
    def buildProtocol(self, addr):
        """
        Builds a protocol, stores a pointer to it and finally returns it.
        This method is called inside Twisted code.
        """
        instance = _CygnusCloudProtocol(self)        
        self.__connections.append(instance)
        return instance   
        
    def removeConnection(self, connection):
        self.__connections.remove(connection)
        
    def isDisconnected(self):
        return self.__connections.getSize() == 0

    def sendPacket(self, packet):
        """
        Returns the last built instance
        Args:
            None
        Returns:
            the last built protocol instance
        """
        i = 0
        while (i < self.__connections.getSize()) :
            self.__connections[i].sendPacket(packet)
            i += 1
    
    def onPacketReceived(self, p):
        """
        Returns the incoming packages queue
        Args:
            None
        Returns:
            The incoming packages queue
        """
        p = _Packet._deserialize(p)
        self.__queue.queue(p.getPriority(), p)
