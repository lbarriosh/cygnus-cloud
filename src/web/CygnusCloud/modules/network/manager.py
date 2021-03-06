# -*- coding: utf8 -*-
'''
Network manager class definitions.
@author: Luis Barrios Hernández
@version: 6.0
'''

from twisted.internet import reactor, ssl
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint, SSL4ServerEndpoint, SSL4ClientEndpoint
from utils1.multithreadingPriorityQueue import GenericThreadSafePriorityQueue
from utils1.multithreadingDictionary import GenericThreadSafeDictionary
from network.packet import _Packet, Packet_TYPE
from network.connection import _NetworkConnection
from network.exceptions.networkManager import NetworkManagerException
from network.threads.dataProcessing import _IncomingDataThread, _OutgoingDataThread
from network.threads.twistedReactor import _TwistedReactorThread
from network.threads.connectionMonitoring import _ConnectionMonitoringThread
from network.protocols import _CygnusCloudProtocolFactory
from time import sleep
        
class NetworkCallback(object):
    """
    A class that represents a network callback object.
    These objects can process an incoming package properly.
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
    UNTIL you KNOW PERFECTLY WELL that you won't be using it again. 
    """
    def __init__(self, certificatesDirectory = None):
        """
        Initializes the NetworkManager's state.
        Args:
            certificatesDirectory: the directory where the certificates are
        """
        self.__connectionPool = GenericThreadSafeDictionary()
        self.__outgoingDataQueue = GenericThreadSafePriorityQueue()
        self.__networkThread = _TwistedReactorThread()        
        self.__outgoingDataThread = _OutgoingDataThread(self.__outgoingDataQueue)
        self.__connectionThread = _ConnectionMonitoringThread(self.__connectionPool)
        self.__certificatesDirectory = certificatesDirectory
        
    def startNetworkService(self):
        """
        Starts the network service. When this operation finishes,
        new connections can be established.
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
        Stops the network service.
        @attention: Due to Twisted related limitations, do NOT stop the network service 
        UNTIL you KNOW PERFECTLY WELL that you won't be using it again. 
        @attention: Remember: there's just one network manager per application, so *please* THINK
        before you stop it.
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
        Allocates the resources associated to a new connection (only if necessary) 
        Args:
            callbackObject: The object that will process all the incoming packages.
        Returns:
            a tuple (queue, thread), where queue and thread are the incoming data queue
            and the incoming data processing thread assigned to this new connection.
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
        
    def connectTo(self, host, port, timeout, callbackObject, useSSL=False):
        """
        Connects to a remote server using its arguments
        @attention: This is a blocking operation. The calling thread will be blocked until
        the connection is established or until a timeout error is detected.
        Args:
            host: host IP address
            port: the port where the host is listenning
            timeout: timeout in seconds. 
            callbackObject: the callback object that will process all the incoming
                packages received through this connection.
        Returns:
            Nothing
        Raises:
            NetworkManagerException: If no answer is received after timeout
                seconds, the connection process will be aborted and a 
                NetworkManagerException will be raised.
        """
        if self.__connectionPool.has_key(port) :
            raise NetworkManagerException("The port " + str(port) +" is already in use")
        # The port is free => proceed
        # Allocate the connection resources
        (queue, thread) = self.__allocateConnectionResources(callbackObject)       
        # Create and configure the endpoint
        factory = _CygnusCloudProtocolFactory(queue)
        if (not useSSL) :
            endpoint = TCP4ClientEndpoint(reactor, host, port, timeout, None)
        else :
            keyPath = self.__certificatesDirectory + "/" + "server.key"
            certificatePath = self.__certificatesDirectory + "/" + "server.crt"
            try :
                endpoint = SSL4ClientEndpoint(reactor, host, port, ssl.DefaultOpenSSLContextFactory(keyPath, certificatePath))
            except Exception:
                raise NetworkManagerException("The key, the certificate or both were not found")
        endpoint.connect(factory)   
        # Wait until the connection is ready
        time = 0
        while factory.isDisconnected() and time <= timeout:            
            sleep(0.01)
            time += 0.01
        if factory.isDisconnected() :
            raise NetworkManagerException("The host " + host + ":" + str(port) +" seems to be unreachable")
        # Create the new connection
        connection = _NetworkConnection(False, port, factory, queue, thread, callbackObject)
        # Add the new connection to the connection pool
        self.__connectionPool[port] = connection
        
    def listenIn(self, port, callbackObject, useSSL=False):
        """
        Creates a server using its arguments.
        @attention: This is a non-blocking operation. Please, check if the connection is ready BEFORE
        you send anything through it.
        Args:
            port: The port to listen in. If it's not free, a NetworkManagerException will be raised.
            callbackObject: the callback object that will process all the incoming
                packages received through this connection.
        Returns:
            Nothing
        """   
        if self.__connectionPool.has_key(port) :
            raise NetworkManagerException("The port " + str(port) +" is already in use") 
        # The port is free => proceed
        # Allocate the connection resources
        (queue, thread) = self.__allocateConnectionResources(callbackObject)       
        # Create and configure the endpoint
        if (not useSSL) :
            endpoint = TCP4ServerEndpoint(reactor, port)       
        else :
            keyPath = self.__certificatesDirectory + "/" + "server.key"
            certificatePath = self.__certificatesDirectory + "/" + "server.crt"
            try :
                endpoint = SSL4ServerEndpoint(reactor, port, ssl.DefaultOpenSSLContextFactory(keyPath, certificatePath))
            except Exception:
                raise NetworkManagerException("The key, the certificate or both were not found")
        factory = _CygnusCloudProtocolFactory(queue)        
        # Create the connection       
        connection = _NetworkConnection(True, port, factory, queue, thread, callbackObject)
        # Create the deferred to retrieve the IListeningPort object
        def registerListeningPort(port):
            connection.setListeningPort(port)
        def onError(failure):
            connection.setError(failure)
        deferred = endpoint.listen(factory)
        deferred.addCallback(registerListeningPort)
        deferred.addErrback(onError)
        connection.setDeferred(deferred)  
        # Register the new connection  
        self.__connectionPool[port] = connection
                
    def isConnectionReady(self, port):
        """
        Checks wether a connection is ready or not.
        Args:
            port: the port assigned to the connection.
        Returns:
            True if the connection is ready or False otherwise.
        Raises:
            NetworkManagerException: a NetworkManagerException will be raised if 
                - there were errors while establishing the connection, or 
                - if the connection was abnormally closed, or
                - if the supplied port is free
        """
        if not self.__connectionPool.has_key(port) :
            raise NetworkManagerException("The port " + str(port) +" is not in use") 
        connection = self.__connectionPool[port]
        self.__detectConnectionErrors(connection)
        return connection.isReady()
    
    def __detectConnectionErrors(self, connection):
        """
        Checks if the given connection is in an error state or was unexpectedly closed.
        Args:
            connection: the connection to monitor.
        Returns:
            Nothing
        """
        if connection.isInErrorState() :
            # Something bad has happened => close the connection, warn the user
            self.__connectionPool.pop(connection.getPort())
            raise NetworkManagerException("Error: " + connection.getError())
        if (connection.wasUnexpectedlyClosed()):
            self.__connectionPool.pop(connection.getPort())
            raise NetworkManagerException("Error: " + "The connection was closed abnormally")
        
    def sendPacket(self, port, packet):
        """
        Sends a packet through the specified port
        Args:
            port: The port assigned to the connection that will be used to send the packet.
            packet: The packet to send.
        Returns:
            Nothing
        Raises:
            NetworkManagerException: a NetworkManagerException will be raised if 
            - there were errors while establishing the connection, or 
            - if the connection was abnormally closed, or
            - if the connection is a server connection and it's not ready yet, or
            - if the supplied port is free
        """
        if not self.__connectionPool.has_key(port) :
            raise NetworkManagerException("There's nothing attached to the port " + str(port))
        connection = self.__connectionPool[port]
        self.__detectConnectionErrors(connection)
        if not connection.isReady() :
            if (connection.isServerConnection()) :
                raise NetworkManagerException("No clients have connected to this port yet")
            else :
                raise NetworkManagerException("The connection is not ready yet")
        connection.registerPacket()
        self.__outgoingDataQueue.queue(packet.getPriority(), (connection, packet))
        
    def createPacket(self, priority):
        """
        Creates an empty data packet and returns it
        Args:
            priority: The new packet's priority. 
        Returns:
            a new data packet.
        Raises:
            NetworkManagerException: this exception will be raised when the packet's priority
            is not a positive integer.
        """
        if not isinstance(priority, int) or  priority < 0 :
            raise NetworkManagerException("Data packets\' priorities MUST be positive integers")
        p = _Packet(Packet_TYPE.DATA, priority)
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
        # Ask the connection to close
        connection.close()
