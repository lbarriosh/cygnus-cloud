# -*- coding: utf8 -*-
'''
In this module we define the NetworkManager class and its main dependencies.
@author: Luis Barrios Hernández
@version: 1.0
'''

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint
from utils.multithreadingPriorityQueue import GenericThreadSafePriorityQueue
from network.packet import Packet, Packet_TYPE
from network.exceptions.networkManager import NetworkManagerException
from network.threads import _IncomingDataThread, _TwistedReactorThread
from network.protocols import _CygnusCloudProtocol, _CygnusCloudProtocolFactory
from time import sleep
        
class NetworkCallback(object):
    """
    A class that represents a network callback object.
    These objects will process the incoming packages.
    """
    def processPacket(self, packet):
        raise NotImplementedError
    
class NetworkManager():
    """
    This class provides a facade to use Twisted in a higher abstraction level way. 
    @attention: Due to some Twisted related limitations, do NOT stop the network service 
    UNTIL you KNOW PERFECTLY WELL that you won\'t be using it again. 
    """
    def __init__(self):
        """
        Initializes the state
        """
        self.__connectionPool = dict();
        self.__networkThread = _TwistedReactorThread()
        
    def startNetworkService(self):
        """
        Starts the reactor thread
        """
        self.__networkThread.start()
        
    def stopNetworkService(self):
        """
        Stops the reactor thread.
        @attention: Due to some Twisted related limitations, do NOT stop the network service 
        UNTIL you KNOW PERFECTLY WELL that you won\'t be using it again. 
        """
        for (_protocol, _queue, thread, _callback) in self.__connectionPool.values() :
            thread.stop()
            thread.join()
        self.__networkThread.stop()
        self.__networkThread.join()
        
    def __allocateConnectionResources(self, callbackObject):
        """
        Allocates (if necessary) the resources associated to a new connection 
        """
        queue = None
        thread = None
        callback = None
        found = False
        for (_protocol, queue, thread, callback) in self.__connectionPool.values() :
            if (callback == callbackObject) :
                # Everything is allocated. Let's reuse it.
                found = True
                break
        if found :
            return (queue, thread)
        else :
            queue = GenericThreadSafePriorityQueue()
            thread = _IncomingDataThread(queue, callbackObject)
            return (queue, thread)
        
    def connectTo(self, host, port, timeout, callbackObject):
        """
        Connects to a remote server using its arguments
        """
        if self.__connectionPool.has_key(port) :
            raise NetworkManagerException("The port " + str(port) +" is already in use")
        # The port is free => proceed
        # Allocate the connection resources
        (queue, thread) = self.__allocateConnectionResources(callbackObject)       
        # Create and configure the endpoint
        factory = _CygnusCloudProtocolFactory(queue)
        endpoint = TCP4ClientEndpoint(reactor, host, port, timeout, None)
        endpoint.connect(factory)   
        time = 0
        while factory.getInstance() is None and time <= timeout:            
            sleep(1)
            time += 1
        if factory.getInstance() is None :
            raise NetworkManagerException("The host " + host + ":" + str(port) +" seems to be unreachable")
        # Add the new connection to the connection pool
        self.__connectionPool[port] = (factory.getInstance(), queue, callbackObject, thread) 
        # Start the thread
        thread.start()
        
    def listenIn(self, port, callbackObject):
        """
        Creates a server using its arguments
        """   
        if self.__connectionPool.has_key(port) :
            raise NetworkManagerException("The port " + str(port) +" is already in use") 
        # The port is free => proceed
        # Allocate the connection resources
        (queue, thread) = self.__allocateConnectionResources(callbackObject)       
        # Create and configure the endpoint
        endpoint = TCP4ServerEndpoint(reactor, port)
        factory = _CygnusCloudProtocolFactory(queue)
        endpoint.listen(factory)
        while factory.getInstance() is None :            
            sleep(1)
        # Add the new connection to the connection pool
        self.__connectionPool[port] = (factory.getInstance(), queue, callbackObject, thread) 
        # Start the thread
        thread.start()
        
    def sendPacket(self, port, packet):
        """
        Sends a packet through the specified port
        """
        if not self.__connectionPool.has_key(port) :
            raise NetworkManagerException("There's nothing attached to the port " + str(port))
        (protocol, _queue, _thread, _callback) = self.__connectionPool[port]
        protocol.sendData(packet)
        
    def createPacket(self, priority):
        """
        Creates an empty data packet and returns it
        """
        if not isinstance(priority, int) or  priority < 0 :
            raise NetworkManagerException("Data packets\' priorities MUST be positive integers")
        p = Packet(Packet_TYPE.DATA, priority)
        return p
        
    def closeConnection(self, port):
        """
        Closes a connection
        """
        if not self.__connectionPool.has_key(port) :
            raise NetworkManagerException("There's nothing attached to the port " + str(port))
        (protocol, _queue, callbackObject, thread) = self.__connectionPool[port]
        protocol.disconnect()
        # Delete the mapping
        self.__connectionPool.pop(port)
        stopThread = True
        for (_protocol, _queue, _thread, callback) in self.__connectionPool.values() :
            if (callbackObject == callback) :
                # The thread is assigned to another connection => we won't stop it now
                stopThread = False
                break
        if stopThread :
            thread.stop()