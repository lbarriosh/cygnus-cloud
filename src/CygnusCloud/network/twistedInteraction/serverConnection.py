'''
Created on 06/03/2013

@author: luis
'''
from connection import Connection, CONNECTION_STATUS
from twisted.internet.endpoints import TCP4ServerEndpoint, SSL4ServerEndpoint
from network.exceptions.connection import ConnectionException
from twisted.internet import reactor, ssl

class ServerConnection(Connection):
    def __init__(self, useSSL, certificatesDirectory, port, queue, incomingDataThread, callbackObject) :
        Connection.__init__(self, useSSL, certificatesDirectory, port, queue, incomingDataThread, callbackObject)

    def establish(self, timeout):
        """
        Establishes a server connection.
        Args:
            None
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
            self._listeningPort = port
        def _onError(failure):
            self.setError(failure)
        self.__deferred = endpoint.listen(self._factory)
        # Configure the deferred object
        self.__deferred.addCallback(_registerListeningPort)
        self.__deferred.addErrback(_onError)     
        
    def getIPAddress(self):
        return ''
    
    def refresh(self):
        if self._status.get() == CONNECTION_STATUS.OPENING :
            if (self._listeningPort != None): 
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
            
    def _freeTwistedResources(self):
        if self._listeningPort is None :                
            self.__deferred.cancel()
        else :
            self._listeningPort.stopListenning()
        Connection._freeTwistedResources(self)