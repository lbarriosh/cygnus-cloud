# -*- coding: UTF8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: clientConnection.py    
    Version: 7.0
    Description: client connection definitions
    
    Copyright 2012-13 Luis Barrios Hernández, Adrián Fernández Hernández,
        Samuel Guayerbas Martín
        
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''
from connection import Connection, CONNECTION_STATUS
from ccutils.enums import enum
from twisted.internet import reactor, ssl
from twisted.internet.endpoints import TCP4ClientEndpoint, SSL4ClientEndpoint
from network.exceptions.connection import ConnectionException
from time import sleep

"""
Reconnection status enum type
"""
RECONNECTION_T = enum("RECONNECTING", "REESTABLISHED", "TIMED_OUT") 

class ClientConnection (Connection) :
    """
    These objects represent client connections
    """ 
    def __init__(self, useSSL, certificatesDirectory, host, port, transferQueue, 
                 incomingDataThread, reconnect, callbackObject):
        """
        Initializes the connection's state
        Args:
            useSSL: if True, all the traffic will be protectd by SSLv4. If false, 
            certificatesDirectory: the directory where the certificates are stored   
            host: the server's hostname or IPv4 address
            port: the port assigned to the connection.
            transferQueue: the incoming data transferQueue assigned to the connection
            incomingDataThread: the incoming data thread assigned to the connection
            reconnect: if True, the network subsystem will try to reestablish the unexpectedly closed client connection.
            callbackObject: the callback object assigned to the connection     
            
        """
        Connection.__init__(self, useSSL, certificatesDirectory, port, transferQueue, incomingDataThread, callbackObject)
        self.__host = host
        self.__reconnect = reconnect
        
    def establish(self, timeout=None):
        """
        Tries to establish a client connection.
        Args:
            timeout: the timeout in seconds
        Returns:
            True if the connection was established, and False if it wasn't.
        """
        Connection.establish(self, timeout)
        # Create and configure the endpoint
        if (not self._useSSL) :
            endpoint = TCP4ClientEndpoint(reactor, self.__host, self._port, timeout, None)
        else :
            keyPath = self._certificatesDirectory + "/" + "server.key"
            certificatePath = self._certificatesDirectory + "/" + "server.crt"
            try :
                endpoint = SSL4ClientEndpoint(reactor, self.__host, self._port, 
                    ssl.DefaultOpenSSLContextFactory(keyPath, certificatePath), timeout)
            except Exception:
                raise ConnectionException("The key, the certificate or both were not found")
        # Establish the connection
        self._deferred = endpoint.connect(self._factory)
        self.__working = True
        def _handleError(error):
            self.__working = False
            self._setError(Connection._prettyPrintTwistedError(error))
        def _handleConnection(error):
            self.__working = False
        self._deferred.addCallback(_handleConnection)
        self._deferred.addErrback(_handleError)
        # Wait until it's ready
        while(self.__working) :
            sleep(0.1)
        return self._error == None
     
    def getHost(self):
        """
        Returns the server's hostname or IPv4 address
        Args:
            None
        Returns:
            The server's IP address. 
        """
        return self.__host
    
    def refresh(self):
        """
        Updates the connection's status
        Args:
            None
        Returns:
            Nothing
        """
        if self._status.get() == CONNECTION_STATUS.OPENING :           
            if (not self._factory.isDisconnected()) :
                # Client => we've got everything we need
                self._status.set(CONNECTION_STATUS.READY)
                self._incomingDataThread.start()           
                
        elif self._status.get() == CONNECTION_STATUS.CLOSING :
            if (self._packagesToSend.read() == 0) :
                # We can close the connection now
                self._close()   
                
        # Check what's happened to the factory
        elif self._status.get() == CONNECTION_STATUS.READY and self._factory.isDisconnected() :
            if (not self.__reconnect) :
                # This connection must be closed *right* now
                self._status.set(CONNECTION_STATUS.CLOSED)
                self._unexpectedlyClosed = True
                self._close()
            else :
                # Try to reconnect to the server
                self.__elapsedTicks = 0
                self.__delay = 1
                self.__reconnections = 0
                self._status.set(CONNECTION_STATUS.RECONNECT)   
                self._freeTwistedResources()
                self._callback.processServerReconnectionData(self.__host, self._port, RECONNECTION_T.RECONNECTING)
                                 
        elif (self._status.get() == CONNECTION_STATUS.RECONNECT) :
            self.__elapsedTicks += 1
            if (self.__elapsedTicks >= self.__delay) :
                # Update the delay and the elapsed ticks
                self.__elapsedTicks = 0
                self.__reconnections += 1
                if (self.__reconnections <= 5) :
                    self.__delay *= 2
                # Try to reconnect to the server NOW 
                if (self.establish(5)) :
                    # We are now connected to the server
                    self._status.set(CONNECTION_STATUS.READY)
                    # Warn the client code
                    self._callback.processServerReconnectionData(self.__host, self._port, RECONNECTION_T.REESTABLISHED) 
                elif (self.__reconnections >= 10) :
                    # Too many reconnection attempts => give up
                    self._close()
                    # Warn the client code
                    self._callback.processServerReconnectionData(self.__host, self._port, RECONNECTION_T.TIMED_OUT) 
                    
    def close(self):
        """
        Closes the connection.
        Args:
            None
        Returns:
            Nothing
        """
        self.__reconnect = False
        Connection.close(self)
                    
    def _freeTwistedResources(self):
        """
        Destroys the twisted-related connection resources.
        Args:
            None
        Returns:
            Nothing
        """
        if (self._factory.isDisconnected()) :
            self._deferred.cancel()
        Connection._freeTwistedResources(self)