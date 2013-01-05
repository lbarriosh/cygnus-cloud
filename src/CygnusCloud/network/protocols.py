'''
Created on Jan 4, 2013

@author: 
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
        """
        self.__incomingPacketsQueue = queue
    
    def dataReceived(self, data):
        """
        Generates a packet with the received data and stores it on the
        incoming priority queue associated with the protocol instance.
        """
        p = Packet._deserialize(data)
        self.__incomingPacketsQueue.queue(p.getPriority(), p)
    
    def connectionMade(self):
        print "Connection established"
    
    def connectionLost(self, reason):
        print "Connection lost"  
    
    def sendData(self, packet):
        """
        Sends the serialized packet
        """
        self.transport.write(packet._serialize())
        
    def disconnect(self):
        """
        Closes the connection
        """
        self.transport.loseConnection()
        
class _CygnusCloudProtocolFactory(Factory):
    """
    Protocol factory. These objects are used to create protocol instances
    within the Twisted Framework.
    """    
    def __init__(self, queue):
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
        """
        return self.__instance
    
    def getIncomingDataQueue(self):
        """
        Returns the incoming packages queue
        """
        return self.__queue
