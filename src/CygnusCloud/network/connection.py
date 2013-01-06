# -*- coding: utf8 -*-
'''
NetworkConnection definitions
@author: Luis Barrios Hernández
@version: 4.0
'''

from utils.enums import enum
from threading import BoundedSemaphore
from utils.multithreadingCounter import MultithreadingCounter

CONNECTION_STATUS = enum("OPENING", "READY", "CLOSING", "CLOSED")

class _ConnectionStatus(object):
    def __init__(self, status):
        self.__status = status
        self.__semaphore = BoundedSemaphore(1)
    def get(self):
        return self.__status
    def set(self, value):
        with self.__semaphore :
            self.__status = value

class NetworkConnection(object):
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
        self.__mustClose = False        
        
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
        self.__factory().getInstance().sendData(p)
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
    
    def refresh(self):
        """
        Updates the connection's status
        Args:
            None
        Returns:
            Nothing
        """
        if self.__status.get() == CONNECTION_STATUS.OPENING :
            if (self.__isServer and self.__listeningPort != None )\
                or (not self.__isServer and self.__factory.getInstance() != None) :
                self.__status.set(CONNECTION_STATUS.READY)
                self.__incomingDataThread.start()   
                
        if self.__status.get() == CONNECTION_STATUS.CLOSING :
            if (self.__packagesToSend.read() == 0) :
                # We can close the connection now
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
           
    def close(self):
        """
        Closes this connection
        Args:
            None
        Returns:
            Nothing
        """    
        self.__status.set(CONNECTION_STATUS.CLOSING)
        
    def __close(self):
        # Ask twisted to close the connection
        if self.__isServer :
            if self.__listeningPort is None :                
                self.__deferred.cancel()
            else :
                if not self.__factory.disconnected() :
                    self.__listeningPort.loseConnection()
        else :
            self.__factory.getInstance().disconnect()
        # Free the connection resources
        self.__incomingDataThread.stop(True)
        self.__status.set(CONNECTION_STATUS.CLOSED)