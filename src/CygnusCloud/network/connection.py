# -*- coding: utf8 -*-
'''
Network connection definitions
@author: Luis Barrios Hernández
@version: 5.0
'''

from utils.enums import enum
from threading import BoundedSemaphore
from utils.multithreadingCounter import MultithreadingCounter

# Connection status enum type
CONNECTION_STATUS = enum("OPENING", "READY_WAIT", "READY", "CLOSING", "CLOSED", "ERROR")

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
    def __init__(self, isServer, port, factory, queue, incomingDataThread, callbackObject):
        """
        Initializes the connection.
        Args:
            isServer: True when this is a server connection or False otherwise.
            port: the port assigned to the connection.  
            factory: the protocol factory assigned to the connnection     
            queue: the incoming data queue assigned to the connection
            incomingDataThread: the incoming data thread assigned to the connection
            callbackObject: the callback object assigned to the connection     
        """
        self.__status = _ConnectionStatus(CONNECTION_STATUS.OPENING)
        self.__isServer = isServer
        self.__port = port
        self.__factory = factory
        self.__queue = queue
        self.__incomingDataThread = incomingDataThread        
        self.__callback = callbackObject
        self.__packagesToSend = MultithreadingCounter()
        self.__deferred = None
        self.__listeningPort = None
        self.__unexpectedlyClosed = False        
        self.__error = None
        
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
        Sends a packet though this connection.
        Args:
            p: the packet to send
        Returns:
            None
        """
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
        return self.__isServer
    
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
                if (not self.__isServer):
                    # Client => we've got everything we need
                    self.__status.set(CONNECTION_STATUS.READY)
                elif (self.__listeningPort != None):
                    # Server => the connection must also have a listening port before
                    # it's ready.
                    self.__status.set(CONNECTION_STATUS.READY_WAIT)
            self.__incomingDataThread.start()
                
        if self.__status.get() == CONNECTION_STATUS.READY_WAIT :
            if not self.__factory.isDisconnected() :
                self.__status.set(CONNECTION_STATUS.READY)
                
        if self.__status.get() == CONNECTION_STATUS.CLOSING :
            if (self.__packagesToSend.read() == 0) :
                # We can close the connection now
                self.__close()   
                
        # Check what's happened to the factory
        if self.__status.get() == CONNECTION_STATUS.READY and self.__factory.isDisconnected() :
            # This connection must be closed *right* now
            self.__status.set(CONNECTION_STATUS.CLOSED)
            self.__unexpectedlyClosed = True
            self.__close()
        
    def setListeningPort(self, listeningPort):
        """
        Set the IListeningPort assigned to a server connection
        Args:
            ListeningPort: the IListeningPort assigned to this connection
        Returns:
            Nothing
        """
        self.__listeningPort = listeningPort
        
    def setDeferred(self, deferred):
        """
        Modifies the deferred object stored in this connection.
        Deferred objects are returned by twisted, and allow us to know when a server connection
        is ready.
        """
        self.__deferred = deferred
        
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
        
    def __close(self):
        """
        Asks twisted to close this connection.
        """
        if self.__isServer :
            if self.__listeningPort is None :                
                self.__deferred.cancel()
            else :
                if not self.__factory.isDisconnected() :
                    self.__listeningPort.loseConnection()
        else :
            self.__factory.disconnect()
        # Free the connection resources
        self.__incomingDataThread.stop(True)
        self.__status.set(CONNECTION_STATUS.CLOSED)