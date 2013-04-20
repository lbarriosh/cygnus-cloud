# -*- coding: utf8 -*-
'''
Server connection definitions
@author: Luis Barrios Hernández
@version: 7.0
'''
from connection import Connection, CONNECTION_STATUS
from twisted.internet.endpoints import TCP4ServerEndpoint, SSL4ServerEndpoint
from network.exceptions.connection import ConnectionException
from twisted.internet import reactor, ssl

class ServerConnection(Connection):
    def __init__(self, useSSL, certificatesDirectory, port, queue, incomingDataThread, callbackObject) :
        """
        Initializes the connection's state
        Args:
            useSSL: if True, all the traffic will be protectd by SSLv4. If false, 
            certificatesDirectory: the directory where the certificates are stored               
            port: the port assigned to the connection.
            queue: the incoming data queue assigned to the connection
            incomingDataThread: the incoming data thread assigned to the connection
            callbackObject: the callback object assigned to the connection     
            
        """
        Connection.__init__(self, useSSL, certificatesDirectory, port, queue, incomingDataThread, callbackObject)
        self.__listenningPort = None

    def establish(self, timeout):
        """
        Establishes a server connection.
        Args:
            timeout: this parameter will be ignored.
        Returns:
            Nothing
        """
        Connection.establish(self, timeout)
        # Create and configure the endpoint
        if (not self._useSSL) :
            endpoint = TCP4ServerEndpoint(reactor, self._port)       
        else :
            keyPath = self._certificatesDirectory + "/" + "server.key"
            certificatePath = self._certificatesDirectory + "/" + "server.crt"
            try :
                endpoint = SSL4ServerEndpoint(reactor, self._port, ssl.DefaultOpenSSLContextFactory(keyPath, certificatePath))
            except Exception:
                raise ConnectionException("The key, the certificate or both were not found")          
        # Establish the connection     
        def _registerListeningPort(port):
            self.__listenningPort = port
        def _onError(error):
            self._setError(Connection._prettyPrintTwistedError(error))
        self._deferred = endpoint.listen(self._factory)
        # Configure the deferred object
        self._deferred.addCallback(_registerListeningPort)
        self._deferred.addErrback(_onError)     
        
    def getHost(self):
        """
        Returns an emtpy string (this is a server connection. Therefore, this machine is its own host).
        """
        return ''
    
    def refresh(self):
        """
        Updates the connection's status
        Args:
            None
        Returns:
            Nothing
        """
        if self._status.get() == CONNECTION_STATUS.OPENING :
            if (self.__listenningPort != None): 
                # Server => the connection must also have a listening port before
                # it's ready.
                self._status.set(CONNECTION_STATUS.READY_WAIT)
                self._incomingDataThread.start()
                
        elif self._status.get() == CONNECTION_STATUS.READY_WAIT :
            if not self._factory.isDisconnected() :
                self._status.set(CONNECTION_STATUS.READY)
                
        elif self._status.get() == CONNECTION_STATUS.CLOSING :
            if (self._packagesToSend.read() == 0) :
                # We can close the connection now
                self._close()   
                
        # Check what's happened to the factory
        elif self._status.get() == CONNECTION_STATUS.READY and self._factory.isDisconnected() :            
            # There are no connected clients, but the connection has not been closed yet
            # => accept new client connections
            self._status.set(CONNECTION_STATUS.READY_WAIT)
            
    def toggleBroadcastMode(self):
        """
        Switches between unicast and broadcast modes. This functionality
        is only available in server connections.
        Args:
            None
        Returns:
            Nothing
        """
        self._factory.toggleBroadcastMode()
            
    def _freeTwistedResources(self):
        """
        Destroys the twisted-related connection resources.
        Args:
            None
        Returns:
            Nothing
        """
        if self.__listenningPort is None :                
            self._deferred.cancel()
        else :
            self.__listenningPort.loseConnection()
        Connection._freeTwistedResources(self)