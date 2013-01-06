# -*- coding: utf8 -*-
'''
NetworkConnection definitions
@author: Luis Barrios Hernández
@version: 2.0
'''

class NetworkConnection(object):
    """
    A class that represents a network connection.
    """
    def __init__(self, isServer, port, protocol, queue, callback, incomingDataThread, deferred = None):
        """
        Initializes the connection.
        Args:
            isServer: True when this is a server connection or False otherwise.
            port: the port assigned to the connection.
            protocol: a Protocol object. This object will be used to send data.
            queue: the incoming data queue.
            callback: the callback object that will process all the incoming packages.
            incomingDataThread: the thread where all the incoming packages will be processed.
            deferred: a Deferred object used to retrieve the IListeningPort associated to a server connection.
        """
        self.__isServer = isServer
        self.__port = port
        self.__protocol = protocol
        self.__queue = queue
        self.__callback = callback
        self.__incomingDataThread = incomingDataThread
        self.__packagesToSend = 0
        self.__deferred = deferred
        self.__listeningPort = None
        self.__waitingThread = None
        self.__disposable = False
        
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
    
    def setWaitingThread(self, thread):
        """
        Sets the waiting thread associated to this connection.
        Args:
            None
        Returns:
            The waiting thread associated to this connection
        """
        self.__waitingThread = thread
    
    def sendPacket(self, p):
        """
        Sends a packet though this connection.
        Args:
            p: the packet to send
        Returns:
            None
        """
        self.__protocol.sendData(p)
        self.__packagesToSend -= 1
        
    def registerPacket(self):
        """
        Registers a packet to send through this connection.
        Args:
            None
        Returns:
            Nothing
        """
        self.__packagesToSend += 1
    
    def setProtocol(self, protocol):
        """
        Sets the protocol assigned to this connection
        Args:
            protocol: the protocol assigned to this connection
        Returns:
            Nothing
        """
        self.__protocol = protocol
    
    def isReady(self):
        """
        Checks if the connection is ready to send data or not
        Args:
            None
        Returns:
            True if the connection is ready to send data, and false otherwise.
        """
        return self.__protocol != None
    
    def getCallback(self):
        """
        Returns the callback object assigned to this connection
        Args:
            None
        Returns:
            The callback object assigned to this connection.
        """
        return self.__callback
    
    def startThread(self):
        """
        Starts the incoming data thread
        Args:
            None
        Returns:
            Nothing
        """
        self.__incomingDataThread.start()
        
    def setListeningPort(self, listeningPort):
        """
        Set the IListeningPort assigned to a server connection
        Args:
            ListeningPort: the IListeningPort assigned to this connection
        Returns:
            Nothing
        """
        self.__listeningPort = listeningPort
    
    def stopThread(self, join):
        """
        Stops the incoming data thread
        Args:
            join: if True, the current thread will wait until the incoming data thread finishes.        
        """
        self.__incomingDataThread.stop()
        if join :
            self.__incomingDataThread.join()
            
    def isDisposable(self):
        """
        Checks if the connection can be safely deleted or not
        Args:
            None
        Returns:
            True if this connection can be safely deleted, and false otherwise.
        """
        return self.__disposable and self.__packagesToSend == 0
    
    def close(self):
        """
        Closes the connection
        Args:
            None
        Returns:
            Nothing
        """
        if self.__isServer :
            if self.__listeningPort is None :
                # La conexión no se ha establecido todavía => cancelar deferred
                self.__deferred.cancel()
                self.__waitingThread.stop()
            else :
                deferred = self.__listeningPort.stopListenning()
                def setDisposable():
                    self.__disposable = True
                deferred.addCallback(setDisposable)
        else :
            self.__protocol.disconnect()
