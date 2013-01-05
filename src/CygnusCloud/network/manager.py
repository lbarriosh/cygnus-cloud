# -*- coding: utf8 -*-
'''
In this module we define the NetworkManager class and its main dependencies.
@author: Luis Barrios Hernández
@version: 1.0
'''

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint
from utils.multithreadingPriorityQueue import GenericThreadSafePriorityQueue
from utils.multithreadingDictionary import GenericThreadSafeDictionary
from utils.multithreadingList import GenericThreadSafeList
from network.packet import Packet, Packet_TYPE
from network.connection import NetworkConnection
from network.exceptions.networkManager import NetworkManagerException
from network.threads.dataProcessing import _IncomingDataThread, _OutgoingDataThread
from network.threads.twistedReactor import _TwistedReactorThread
from network.threads.server import _ServerWaitThread
from network.threads.closedconnection import _ClosedConnectionThread
from network.protocols import _CygnusCloudProtocolFactory
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
        self.__connectionPool = GenericThreadSafeDictionary()
        self.__networkThread = _TwistedReactorThread()
        self.__outgoingDataQueue = GenericThreadSafePriorityQueue()
        self.__outgoingDataThread = _OutgoingDataThread(self.__outgoingDataQueue)
        self.__connectionsToDelete = GenericThreadSafeList()
        self.__portsToBeFreed = GenericThreadSafeList()
        self.__connectionThread = _ClosedConnectionThread(self.__connectionsToDelete, self.__portsToBeFreed)
        
    def startNetworkService(self):
        """
        Starts the reactor thread
        """
        self.__networkThread.start()
        self.__outgoingDataThread.start()
        self.__connectionThread.start()
        
    def stopNetworkService(self):
        """
        Stops the reactor thread.
        @attention: Due to some Twisted related limitations, do NOT stop the network service 
        UNTIL you KNOW PERFECTLY WELL that you won\'t be using it again. 
        """
        for connection in self.__connectionPool.values() :
            connection.close()
            connection.stopThread(True)
        self.__connectionThread.stop()
        self.__outgoingDataThread.stop()
        self.__outgoingDataThread.join()
        self.__networkThread.stop()
        self.__networkThread.join()
        
    def __allocateConnectionResources(self, callbackObject):
        """
        Allocates (if necessary) the resources associated to a new connection 
        """
        c = None
        for connection in self.__connectionPool.values() :
            if (connection.getCallback() == callbackObject) :
                # Everything is allocated. Let's reuse it.
                c = connection
                break
        if c != None :
            return (c.getQueue(), c.getThread())
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
        if self.__portsToBeFreed.count(port) != 0 :
            raise NetworkManagerException("The port " + str(port) + " is not free yet")
        # The port is free => proceed
        # Allocate the connection resources
        (queue, thread) = self.__allocateConnectionResources(callbackObject)       
        # Create and configure the endpoint
        factory = _CygnusCloudProtocolFactory(queue)
        endpoint = TCP4ClientEndpoint(reactor, host, port, timeout, None)
        endpoint.connect(factory)   
        time = 0
        while factory.getInstance() is None and time <= timeout:            
            sleep(0.001)
            time += 0.001
        if factory.getInstance() is None :
            raise NetworkManagerException("The host " + host + ":" + str(port) +" seems to be unreachable")
        # Add the new connection to the connection pool
        self.__connectionPool[port] = NetworkConnection(False, port, factory.getInstance(), queue, callbackObject, thread)
        # Start the connection thread
        thread.start()
        
    def listenIn(self, port, callbackObject):
        """
        Creates a server using its arguments
        """   
        if self.__connectionPool.has_key(port) :
            raise NetworkManagerException("The port " + str(port) +" is already in use") 
        if self.__portsToBeFreed.count(port) != 0 :
            raise NetworkManagerException("The port " + str(port) + " is not free yet")
        # The port is free => proceed
        # Allocate the connection resources
        (queue, thread) = self.__allocateConnectionResources(callbackObject)       
        # Create and configure the endpoint
        endpoint = TCP4ServerEndpoint(reactor, port)       
        factory = _CygnusCloudProtocolFactory(queue)        
        # Create the connection and the deferred
        deferred = endpoint.listen(factory)
        connection = NetworkConnection(True, port, None, queue, callbackObject, thread, deferred)
        def registerListeningPort(port):
            connection.setListeningPort(port)
        deferred.addCallback(registerListeningPort)    
        self.__connectionPool[port] = connection
        # Create the waiting thread
        th = _ServerWaitThread(factory, connection.setProtocol, connection.startThread)
        # Register it
        connection.setWaitingThread(th)
        # And finally, start it
        th.start()
        
    def isConnectionReady(self, port):
        if not self.__connectionPool.has_key(port) :
            raise NetworkManagerException("The port " + str(port) +" is not in use") 
        connection = self.__connectionPool[port]
        return connection.isReady()
        
    def sendPacket(self, port, packet):
        """
        Sends a packet through the specified port
        """
        if not self.__connectionPool.has_key(port) :
            raise NetworkManagerException("There's nothing attached to the port " + str(port))
        connection = self.__connectionPool[port]
        if not connection.isReady() :
            raise NetworkManagerException("No clients have connected to this port yet")
        connection.registerPacket()
        self.__outgoingDataQueue.queue(packet.getPriority(), (connection, packet))
        
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
        connection = self.__connectionPool[port]
        connection.close()
        self.__connectionsToDelete.append(connection)
        self.__portsToBeFreed.append(connection.getPort())
        callback = connection.getCallback()
        # Delete the mapping
        self.__connectionPool.pop(port)
        stopThread = True
        for connection in self.__connectionPool.values() :
            if (connection.getCallback() == callback) :
                # The thread is assigned to another connection => we won't stop it now
                stopThread = False
                break
        if stopThread :
            connection.stopThread(False)