# -*- coding: utf8 -*-
'''
Network connection definitions
@author: Luis Barrios Hernández
@version: 6.1
'''

from ccutils.enums import enum
from connectionStatus import ConnectionStatus
from protocols import CygnusCloudProtocolFactory
from ccutils.multithreadingCounter import MultithreadingCounter

"""
Connection status enum type.
"""
CONNECTION_STATUS = enum("OPENING", "READY_WAIT", "READY", "CLOSING", "CLOSED", "ERROR", "RECONNECT")



class Connection(object):
    """
    A class that represents a network connection.
    """
    def __init__(self, useSSL, certificatesDirectory, port, queue, incomingDataThread, callbackObject):
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
        self._status = ConnectionStatus(CONNECTION_STATUS.OPENING)
        self._useSSL = useSSL
        self._certificatesDirectory = certificatesDirectory
        self._port = port
        self._factory = None
        self._queue = queue
        self._incomingDataThread = incomingDataThread        
        self._callback = callbackObject
        self._packagesToSend = MultithreadingCounter()
        self._deferred = None
        self._unexpectedlyClosed = False        
        self._error = None
        
    def establish(self, timeout=None):
        """
        Tries to establish the network connection.
        Args:
            timeout: the timeout in seconds. This argument will only be used with client
            connections.
        Returns:
            True if the connection could be established. Otherwise, it will return false.
        """
        self._factory = CygnusCloudProtocolFactory(self._queue)      
        
    def getIPAddress(self):
        """
        Returns the server's IP address
        Args:
            None
        Returns:
            The server's IP address. If this machine is a server, then 127.0.0.1
            will be returned.
        """
        raise NotImplementedError
        
    def getPort(self):
        """
        Returns the port assigned to this connection.
        Args:
            None
        Returns:
            The port assigned to this connection.
        """
        return self._port
        
    def getQueue(self):
        """
        Returns the incoming data queue assigned to this connection.
        Args:
            None
        Returns:
            The incoming data queue assigned to this connection            
        """
        return self._queue    
    
    def getThread(self):
        """
        Returns the incoming data processing thread assigned to this connection
        Args:
            None
        Returns:
            The incoming data processing thread assigned to this connection
        """
        return self._incomingDataThread
    
    def getCallback(self):
        """
        Returns the callback object assigned to this connection
        Args:
            None
        Returns:
            The callback object assigned to this connection.
        """
        return self._callback    
    
    def getStatus(self):
        """
        Returns the connection status
        Args:
            None
        Returns:
            The connection status
        """
        return self._status.get()
    
    def sendPacket(self, p):
        """
        Sends a packet though this connection. If the connection is closed, the packet will be discarded.
        Args:
            p: the packet to send
        Returns:
            Nothing
        """
        if (self._status.get() == CONNECTION_STATUS.READY or self._status.get() == CONNECTION_STATUS.CLOSING) :           
            self._factory.sendPacket(p)
            self._packagesToSend.decrement()
            return True
                
    def registerPacket(self):
        """
        Registers a packet to be sent through this connection.
        Args:
            None
        Returns:
            Nothing
        """
        self._packagesToSend.increment()
    
    
    def isReady(self):
        """
        Checks if the connection is ready to send data or not
        Args:
            None
        Returns:
            True if the connection is ready to send data, and false otherwise.
        """
        return self._status.get() == CONNECTION_STATUS.READY
    
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
        raise NotImplementedError
        
    def isInErrorState(self):
        """
        Checks if the connection is in an error state.
        """
        return self._status.get() == CONNECTION_STATUS.ERROR
    
    def wasUnexpectedlyClosed(self):
        """
        Checks if the connection was unexpectedly closed. The connection may be closed unexpectedly
        in two different ways:
            1) All the clients disconnect from a server.
            2) A server disconnects from all its clients.
        """
        return self._unexpectedlyClosed
        
    def getError(self):
        """
        Returns the error message stored in this connection.
        """
        return self._error
    
    def _setError(self, value):
        """
        Modifies the error message stored in this connection.
        """
        self._status.set(CONNECTION_STATUS.ERROR)
        self._error = value
           
    def close(self):
        """
        Asks this connection to close
        Args:
            None
        Returns:
            Nothing
        """    
        self._status.set(CONNECTION_STATUS.CLOSING)
        
    def _freeTwistedResources(self):
        """
        Destroys the twisted-related connection resources.
        Args:
            None
        Returns:
            Nothing
        """
        self._factory.disconnect()
        
    def _close(self):
        """
        Closes this connection.
        Args:
            None
        Returns:
            Nothing
        """
        # Free the connection resources
        self._freeTwistedResources()
        self._incomingDataThread.stop(True)
        self._status.set(CONNECTION_STATUS.CLOSED)