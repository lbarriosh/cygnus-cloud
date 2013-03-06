'''
Created on 06/03/2013

@author: luis
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
    def __init__(self, useSSL, certificatesDirectory, ipAddr, port, queue, 
                 incomingDataThread, reconnect, callbackObject):
        Connection.__init__(self, useSSL, certificatesDirectory, port, queue, incomingDataThread, callbackObject)
        self.__ipAddr = ipAddr
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
            endpoint = TCP4ClientEndpoint(reactor, self.__ipAddr, self._port, timeout, None)
        else :
            keyPath = self._certificatesDirectory + "/" + "server.key"
            certificatePath = self._certificatesDirectory + "/" + "server.crt"
            try :
                endpoint = SSL4ClientEndpoint(reactor, self.__ipAddr, self._port, 
                    ssl.DefaultOpenSSLContextFactory(keyPath, certificatePath), timeout)
            except Exception:
                raise ConnectionException("The key, the certificate or both were not found")
        # Establish the connection
        self._deferred = endpoint.connect(self._factory)
        self.__working = True
        def _handleError(error):
            self.__working = False
            self._setError(error)
        def _handleConnection(error):
            self.__working = False
        self._deferred.addCallback(_handleConnection)
        self._deferred.addErrback(_handleError)
        # Wait until it's ready
        while(self.__working) :
            sleep(0.1)
        return self._error == None
     
    def getIPAddress(self):
        return self.__ipAddr
    
    def refresh(self):
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
                self._callback.processServerReconnectionData(self.__ipAddr, self._port, RECONNECTION_T.RECONNECTING)
                                 
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
                    self._callback.processServerReconnectionData(self.__ipAddr, self._port, RECONNECTION_T.REESTABLISHED) 
                elif (self.__reconnections >= 10) :
                    # Too many reconnection attempts => give up
                    self._close()
                    # Warn the client code
                    self._callback.processServerReconnectionData(self.__ipAddr, self._port, RECONNECTION_T.TIMED_OUT) 
                    
    def close(self):
        self.__reconnect = False
        Connection.close(self)
                    
    def _freeTwistedResources(self):
        if (self._factory.isDisconnected()) :
            self._deferred.cancel()
        Connection._freeTwistedResources(self)