# -*- coding: utf8 -*-
'''
Network connection definitions
@author: Luis Barrios Hernández
@version: 6.1
'''

from ccutils.enums import enum
from network.exceptions.connection import ConnectionException
from threading import BoundedSemaphore
from protocols import _CygnusCloudProtocolFactory
from ccutils.multithreadingCounter import MultithreadingCounter
from twisted.internet.endpoints import TCP4ClientEndpoint, TCP4ServerEndpoint, SSL4ServerEndpoint, SSL4ClientEndpoint
from twisted.internet import reactor, ssl
from time import sleep

"""
Connection status enum type.
"""
CONNECTION_STATUS = enum("OPENING", "READY_WAIT", "READY", "CLOSING", "CLOSED", "ERROR", "RECONNECT")

"""
Reconnection status enum type
"""
RECONNECTION_T = enum("RECONNECTING", "REESTABLISHED", "TIMED_OUT") 

class _ConnectionStatus(object):
    """
    A class that stores a connection's status and allows its modification
    in a thread-safe manner.
    """
    def __init__(self, status):
        """
        Initializes the status using its argument.
        """
        self.__status = status
        self.__semaphore = BoundedSemaphore(1)
    def get(self):
        """
        Returns the status value
        """
        return self.__status
    def set(self, value):
        """
        Modifies the status.
        """
        with self.__semaphore :
            self.__status = value

class _NetworkConnection(object):
    """
    A class that represents a network connection.
    """
    def __init__(self, isServerConnection, useSSL, certificatesDirectory, ipAddr, port, queue, incomingDataThread, reconnect, callbackObject):
        """
        Initializes the connection.
        Args:
            isServerConnection: True when this is a server connection or False otherwise.
            ipAddr: the server's IP address
            port: the port assigned to the connection.   
            queue: the incoming data queue assigned to the connection
            incomingDataThread: the incoming data thread assigned to the connection
            reconnect: if True, the network subsystem will try to reestablish the unexpectedly closed client connection.
            This argument will be ignored if this is a server connection. 
            callbackObject: the callback object assigned to the connection     
        """
        self.__status = _ConnectionStatus(CONNECTION_STATUS.OPENING)
        self.__isServerConnection = isServerConnection
        self.__useSSL = useSSL
        self.__certificatesDirectory = certificatesDirectory
        self.__ipAddr = ipAddr
        self.__port = port
        self.__factory = None
        self.__queue = queue
        self.__incomingDataThread = incomingDataThread        
        self.__callback = callbackObject
        self.__packagesToSend = MultithreadingCounter()
        self.__deferred = None
        self.__listeningPort = None
        self.__unexpectedlyClosed = False        
        self.__error = None
        self.__reconnect = reconnect
        
    def establish(self, timeout=None):
        """
        Tries to establish the network connection.
        Args:
            timeout: the timeout in seconds. This argument will only be used with client
            connections.
        Returns:
            True if the connection could be established. Otherwise, it will return false.
        """
        if self.__isServerConnection :
            self.__establishServerConnection()
            return True
        else :
            return self.__establishClientConnection(timeout)
        
    def __establishClientConnection(self, timeout):
        """
        Tries to establish a client connection.
        Args:
            timeout: the timeout in seconds
        Returns:
            True if the connection was established, and False if it wasn't.
        """
        # Create and configure the endpoint
        self.__factory = _CygnusCloudProtocolFactory(self.__queue)
        if (not self.__useSSL) :
            endpoint = TCP4ClientEndpoint(reactor, self.__ipAddr, self.__port, timeout, None)
        else :
            keyPath = self.__certificatesDirectory + "/" + "server.key"
            certificatePath = self.__certificatesDirectory + "/" + "server.crt"
            try :
                endpoint = SSL4ClientEndpoint(reactor, self.__ipAddr, self.__port, ssl.DefaultOpenSSLContextFactory(keyPath, certificatePath))
            except Exception:
                raise ConnectionException("The key, the certificate or both were not found")
        # Establish the connection
        endpoint.connect(self.__factory)
        # Wait until it's ready
        time = 0
        while self.__factory.isDisconnected() and time <= timeout:            
            sleep(0.01)
            time += 0.01
        return not self.__factory.isDisconnected()
    
    def __establishServerConnection(self):
        """
        Establishes a server connection.
        Args:
            None
        Returns:
            Nothing
        """
        # Create and configure the endpoint
        if (not self.__useSSL) :
            endpoint = TCP4ServerEndpoint(reactor, self.__port)       
        else :
            keyPath = self.__certificatesDirectory + "/" + "server.key"
            certificatePath = self.__certificatesDirectory + "/" + "server.crt"
            try :
                endpoint = SSL4ServerEndpoint(reactor, self.__port, ssl.DefaultOpenSSLContextFactory(keyPath, certificatePath))
            except Exception:
                raise ConnectionException("The key, the certificate or both were not found")
        self.__factory = _CygnusCloudProtocolFactory(self.__queue)   
        # Establish the connection     
        def _registerListeningPort(port):
            self.__listeningPort = port
        def _onError(failure):
            self.setError(failure)
        self.__deferred = endpoint.listen(self.__factory)
        # Configure the deferred object
        self.__deferred.addCallback(_registerListeningPort)
        self.__deferred.addErrback(_onError)        
        
    def getIPAddress(self):
        """
        Returns the server's IP address
        Args:
            None
        Returns:
            The server's IP address. If this machine is a server, then 127.0.0.1
            will be returned.
        """
        return self.__ipAddr
        
    def getPort(self):
        """
        Returns the port assigned to this connection.
        Args:
            None
        Returns:
            The port assigned to this connection.
        """
        return self.__port
        
    def getQueue(self):
        """
        Returns the incoming data queue assigned to this connection.
        Args:
            None
        Returns:
            The incoming data queue assigned to this connection            
        """
        return self.__queue    
    
    def getThread(self):
        """
        Returns the incoming data processing thread assigned to this connection
        Args:
            None
        Returns:
            The incoming data processing thread assigned to this connection
        """
        return self.__incomingDataThread
    
    def getCallback(self):
        """
        Returns the callback object assigned to this connection
        Args:
            None
        Returns:
            The callback object assigned to this connection.
        """
        return self.__callback    
    
    def getStatus(self):
        """
        Returns the connection status
        Args:
            None
        Returns:
            The connection status
        """
        return self.__status.get()
    
    def sendPacket(self, p):
        """
        Sends a packet though this connection. If the connection is closed, the packet will be discarded.
        Args:
            p: the packet to send
        Returns:
            None
        """
        if (self.__status.get() == CONNECTION_STATUS.READY or self.__status.get() == CONNECTION_STATUS.CLOSING) :           
            self.__factory.sendPacket(p)
            self.__packagesToSend.decrement()
                
    def registerPacket(self):
        """
        Registers a packet to be sent through this connection.
        Args:
            None
        Returns:
            Nothing
        """
        self.__packagesToSend.increment()
    
    
    def isReady(self):
        """
        Checks if the connection is ready to send data or not
        Args:
            None
        Returns:
            True if the connection is ready to send data, and false otherwise.
        """
        return self.__status.get() == CONNECTION_STATUS.READY
    
    def isServerConnection(self):
        """
        Determines if this is a server connection or not.
        Args:
            None
        Returns:
            True if this connection is a server one, and false if it isn't.
        """
        return self.__isServerConnection
    
    def refresh(self):
        """
        Updates the connection's status
        Args:
            None
        Returns:
            Nothing
        """
        if self.__status.get() == CONNECTION_STATUS.OPENING :
            if (not self.__factory.isDisconnected()) :
                if (not self.__isServerConnection):
                    # Client => we've got everything we need
                    self.__status.set(CONNECTION_STATUS.READY)
                elif (self.__listeningPort != None):
                    # Server => the connection must also have a listening port before
                    # it's ready.
                    self.__status.set(CONNECTION_STATUS.READY_WAIT)
                self.__incomingDataThread.start()
                
        elif self.__status.get() == CONNECTION_STATUS.READY_WAIT :
            if not self.__factory.isDisconnected() :
                self.__status.set(CONNECTION_STATUS.READY)
                
        elif self.__status.get() == CONNECTION_STATUS.CLOSING :
            if (self.__packagesToSend.read() == 0) :
                # We can close the connection now
                self.__close()   
                
        # Check what's happened to the factory
        elif self.__status.get() == CONNECTION_STATUS.READY and self.__factory.isDisconnected() :
            if (self.__isServerConnection) :
                # There are no connected clients, but the connection has not been closed yet
                # => accept new client connections
                self.__status.set(CONNECTION_STATUS.READY_WAIT)
            else :
                if (not self.__reconnect) :
                    # This connection must be closed *right* now
                    self.__status.set(CONNECTION_STATUS.CLOSED)
                    self.__unexpectedlyClosed = True
                    self.__close()
                else :
                    # Try to reconnect to the server
                    self.__elapsedTicks = 0
                    self.__delay = 1
                    self.__reconnections = 0
                    self.__status.set(CONNECTION_STATUS.RECONNECT)   
                    self.__destroyTwistedResources()
                    self.__callback.processServerReconnectionData(self.__ipAddr, self.__port, RECONNECTION_T.RECONNECTING)
                                 
        elif (self.__status.get() == CONNECTION_STATUS.RECONNECT) :
            self.__elapsedTicks += 1
            if (self.__elapsedTicks >= self.__delay) :
                # Update the delay and the elapsed ticks
                self.__elapsedTicks = 0
                self.__reconnections += 1
                if (self.__reconnections <= 5) :
                    self.__delay *= 2
                # Try to reconnect to the server NOW 
                if (self.__establishClientConnection(5)) :
                    # We are now connected to the server
                    self.__status.set(CONNECTION_STATUS.READY)
                    # Warn the client code
                    self.__callback.processServerReconnectionData(self.__ipAddr, self.__port, RECONNECTION_T.REESTABLISHED) 
                elif (self.__reconnections >= 10) :
                    # Too many reconnection attempts => give up
                    self.__close()
                    # Warn the client code
                    self.__callback.processServerReconnectionData(self.__ipAddr, self.__port, RECONNECTION_T.TIMED_OUT) 
        
    def isInErrorState(self):
        """
        Checks if the connection is in an error state.
        """
        return self.__status.get() == CONNECTION_STATUS.ERROR
    
    def wasUnexpectedlyClosed(self):
        """
        Checks if the connection was unexpectedly closed. The connection may be closed unexpectedly
        in two different ways:
            1) All the clients disconnect from a server.
            2) A server disconnects from all its clients.
        """
        return self.__unexpectedlyClosed
        
    def getError(self):
        """
        Returns the error message stored in this connection.
        """
        return self.__error
    
    def setError(self, value):
        """
        Modifies the error message stored in this connection.
        """
        self.__status.set(CONNECTION_STATUS.ERROR)
        self.__error = value
           
    def close(self):
        """
        Asks this connection to close
        Args:
            None
        Returns:
            Nothing
        """    
        self.__status.set(CONNECTION_STATUS.CLOSING)
        
    def __destroyTwistedResources(self):
        """
        Destroys the twisted-related connection resources.
        Args:
            None
        Returns:
            Nothing
        """
        if self.__isServerConnection :
            if self.__listeningPort is None :                
                self.__deferred.cancel()
            else :
                if not self.__factory.isDisconnected() :
                    self.__listeningPort.loseConnection()
        else :
            self.__factory.disconnect()
        
    def __close(self):
        """
        Closes this connection.
        Args:
            None
        Returns:
            Nothing
        """
        self.__destroyTwistedResources()
        # Free the connection resources
        self.__incomingDataThread.stop(True)
        self.__status.set(CONNECTION_STATUS.CLOSED)