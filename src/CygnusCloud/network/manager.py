# -*- coding: utf8 -*-
'''
Network manager class definitions.
@author: Luis Barrios Hernández
@version: 4.0
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
from network.threads.connectionMonitoring import _ConnectionMonitoringThread
from network.protocols import _CygnusCloudProtocolFactory
from time import sleep
        
class NetworkCallback(object):
    """
    A class that represents a network callback object.
    These objects will process the incoming packages.
    """
    def processPacket(self, packet):
        """
        Processes an incoming packet
        Args:
            packet: the packet to process
        Returns:
            Nothing
        
        """
        raise NotImplementedError   

class NetworkManager():
    """
    This class provides a facade to use Twisted in a higher abstraction level way.    
    @attention: If you don't want everything to conk out, DO NOT USE MORE THAN
    ONE NetworkManager IN THE SAME PROGRAM.
    @attention: Due to some Twisted related limitations, do NOT stop the network service 
    UNTIL you KNOW PERFECTLY WELL that you won\'t be using it again. 
    """
    def __init__(self):
        """
        Initializes the NetworkManager.
        Args:
            None
        """
        self.__connectionPool = GenericThreadSafeDictionary()
        self.__portsToBeFreed = GenericThreadSafeList()
        self.__outgoingDataQueue = GenericThreadSafePriorityQueue()
        self.__networkThread = _TwistedReactorThread()        
        self.__outgoingDataThread = _OutgoingDataThread(self.__outgoingDataQueue)
        self.__connectionThread = _ConnectionMonitoringThread(self.__connectionPool, self.__portsToBeFreed)
        
    def startNetworkService(self):
        """
        Starts the reactor thread
        Args:
            None
        Returns:
            Nothing
        """
        self.__networkThread.start()
        self.__outgoingDataThread.start()
        self.__connectionThread.start()
        
    def stopNetworkService(self):
        """
        Stops the reactor thread.
        @attention: Due to some Twisted related limitations, do NOT stop the network service 
        UNTIL you KNOW PERFECTLY WELL that you won\'t be using it again. 
        Args:
            None
        Returns:
            Nothing
        """
        for connection in self.__connectionPool.values() :
            self.closeConnection(connection.getPort())
        self.__outgoingDataThread.stop()
        self.__outgoingDataThread.join()
        self.__connectionThread.stop()
        self.__connectionThread.join()
        self.__networkThread.stop()
        self.__networkThread.join()
        
    def __allocateConnectionResources(self, callbackObject):
        """
        Allocates (if necessary) the resources associated to a new connection 
        Args:
            callbackObject: The object that will process all the incoming packages.
        Returns:
            a tuple (queue, thread), where queue and thread are the incoming data queue
            and the incoming data processing thread assigned to this connection.
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
        Args:
            host: host IP address
            port: the port where the host is listenning
            timeout: timeout in seconds. If no answer is received after timeout
                seconds, the connection process will be aborted and a 
                NetworkManagerException will be raised.
            callbackObject: the callback object that will process all the incoming
                packages received through this connection.
        Returns:
            Nothing
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
        # Wait until the connection is ready
        time = 0
        while factory.getInstance() is None and time <= timeout:            
            sleep(0.001)
            time += 0.001
        if factory.getInstance() is None :
            raise NetworkManagerException("The host " + host + ":" + str(port) +" seems to be unreachable")
        # Create the new connection
        connection = NetworkConnection(False, port, factory, queue, thread, callbackObject)
        # Add the new connection to the connection pool
        self.__connectionPool[port] = connection
        
    def listenIn(self, port, callbackObject):
        """
        Creates a server using its arguments
        Args:
            port: The port to listen in. If it's not free, a NetworkManagerException will be raised.
            callbackObject: the callback object that will process all the incoming
                packages received through this connection.
        Returns:
            Nothing
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
        # Create the connection       
        connection = NetworkConnection(True, port, factory, queue, thread, callbackObject)
        # Create the deferred to retrieve the IListeningPort object
        def registerListeningPort(port):
            connection.setListeningPort(port)
        deferred = endpoint.listen(factory)
        deferred.addCallback(registerListeningPort)  
        # Register the new connection  
        self.__connectionPool[port] = connection
        
    def isConnectionReady(self, port):
        """
        Checks wether a connection is ready or not.
        Args:
            port: the port assigned to the connection. If it\'s free, a NetworkManagerException
            will be raised.
        Returns:
            True if the connection is ready or False otherwise.
        """
        if not self.__connectionPool.has_key(port) :
            raise NetworkManagerException("The port " + str(port) +" is not in use") 
        connection = self.__connectionPool[port]
        return connection.isReady()
        
    def sendPacket(self, port, packet):
        """
        Sends a packet through the specified port
        Args:
            port: The port assigned to the connection that will be used to send the packet.
                If this port is free or this machine is a server and no clients have connected
                to this port, a NetworkManagerException will be raised.
            packet: The packet to send.
        Returns:
            Nothing
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
        Args:
            priority: The new packet's priority. If it's not a positive integar, a NetworkManagerException
            will be raised
        Returns:
            a new data packet.
        """
        if not isinstance(priority, int) or  priority < 0 :
            raise NetworkManagerException("Data packets\' priorities MUST be positive integers")
        p = Packet(Packet_TYPE.DATA, priority)
        return p
        
    def closeConnection(self, port):
        """
        Closes a connection
        Args:
            port: The port assigned to the connection. If it's free, a NetworkManagerException will be
            raised.
        Returns:
            Nothing
        """
        if not self.__connectionPool.has_key(port) :
            raise NetworkManagerException("There's nothing attached to the port " + str(port))
        # Retrieve the connection
        connection = self.__connectionPool[port]       
        # The port is not free yet.
        self.__portsToBeFreed.append(connection.getPort())       
        # Ask the connection to close
        connection.close()