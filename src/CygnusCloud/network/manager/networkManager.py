# -*- coding: utf8 -*-
'''
Network manager class definitions.
@author: Luis Barrios Hernández
@version: 7.1
'''
from twisted.internet import reactor
from ccutils.multithreadingPriorityQueue import GenericThreadSafePriorityQueue
from ccutils.multithreadingDictionary import GenericThreadSafeDictionary
from network.packets.packet import _Packet, Packet_TYPE
from network.twistedInteraction.clientConnection import ClientConnection, RECONNECTION_T
from network.twistedInteraction.serverConnection import ServerConnection
from network.exceptions.networkManager import NetworkManagerException
from network.exceptions.connection import ConnectionException
from network.threads.dataProcessing import IncomingDataThread, OutgoingDataThread
from network.threads.twistedReactor import TwistedReactorThread
from network.threads.connectionMonitoring import ConnectionMonitoringThread
        
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
    
    def processServerReconnectionData(self, ipAddress, port, reconnection_status):
        """
        Processes a server reconnection error.
        Args:
            ipAddress: the server's IPv4 address
            port: the server's port
            reconnection_status: an enum value containing the reconnection status
        Returns:
            Nothing
        """
        if (reconnection_status == RECONNECTION_T.REESTABLISHED):
            string = "Connection reestablished" 
        elif (reconnection_status == RECONNECTION_T.TIMED_OUT):
            string = "Connection timed out"
        else :
            string = "Reconnecting"
  
        print ipAddress + " " + str(port) + " " + string

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
            certificatesDirectory: the directory where the files server.crt and server.key are.
        """
        self.__connectionPool = GenericThreadSafeDictionary()
        self.__outgoingDataQueue = GenericThreadSafePriorityQueue()
        if (not reactor.running) :
            self.__networkThread = TwistedReactorThread()    
        else :
            self.__networkThread = None    
        self.__outgoingDataThread = OutgoingDataThread(self.__outgoingDataQueue)
        self.__connectionThread = ConnectionMonitoringThread(self.__connectionPool)
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
        if (self.__networkThread != None) :
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
        @attention: If this method is called from a network thread, your application will HANG. 
        Please, call it from your application's MAIN thread.
        Args:
            None
        Returns:
            Nothing
        """
        for connection in self.__connectionPool.values() :
            self.closeConnection(connection.getIPAddress(), connection.getPort())
        self.__connectionThread.stop()
        self.__connectionThread.join()
        self.__outgoingDataThread.stop()
        self.__outgoingDataThread.join()
        if (self.__networkThread != None) :
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
            thread = IncomingDataThread(queue, callbackObject)
            return (queue, thread)  
                
    def connectTo(self, host, port, timeout, callbackObject, useSSL=False, reconnect=False):
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
            useSSL: if True, the SSL version 4 protocol will be used. Otherwise, we'll stick
                to TCP version 4.
            reconnect: if True, the network subsystem will try to reconnect to the server
                when the connection is lost.
        Returns:
            Nothing
        Raises:
            NetworkManagerException: If no answer is received after timeout
                seconds, the connection process will be aborted and a 
                NetworkManagerException will be raised.
        """
        if self.__connectionPool.has_key((host,port)) :
            raise NetworkManagerException("The port " + str(port) +" is already in use")
        # The port is free => proceed
        # Allocate the connection resources
        (queue, thread) = self.__allocateConnectionResources(callbackObject)   
        # Create the NetworkConnection object
        connection = ClientConnection(useSSL, self.__certificatesDirectory, host, port, queue, thread, reconnect, callbackObject)
        # Try to establish the connection
        try :
            if (connection.establish(timeout)) :
                # The connection could be created => add it to the connection pool
                self.__connectionPool[(host, port)] = connection
            else :
                # Raise an exception
                raise NetworkManagerException("Error: " + connection.getError())
        except ConnectionException as e:
            raise NetworkManagerException(str(e))
        
    def listenIn(self, port, callbackObject, useSSL=False):
        """
        Creates a server using its arguments.
        @attention: This is a non-blocking operation. Please, check if the connection is ready BEFORE
        you send anything through it.
        Args:
            port: The port to listen in. If it's not free, a NetworkManagerException will be raised.
            callbackObject: the callback object that will process all the incoming
                packages received through this connection.
            useSSL: if True, the SSL version 4 protocol will be used. Otherwise, we'll stick
                to TCP version 4.
        Returns:
            Nothing
        """   
        if self.__connectionPool.has_key(('127.0.0.1', port)) :
            raise NetworkManagerException("The port " + str(port) +" is already in use") 
        # The port is free => proceed
        # Allocate the connection resources
        (queue, thread) = self.__allocateConnectionResources(callbackObject)    
        # Create the NetworkConnection object
        connection = ServerConnection(useSSL, self.__certificatesDirectory, port, queue, thread, callbackObject)
        try :
            # Establish it
            connection.establish(None)
            if (connection.getError() == None) :
                # Register the new connection 
                self.__connectionPool[('', port)] = connection
            else :
                raise ConnectionException(str(connection.getError()))
        except ConnectionException as e:
            raise NetworkManagerException(str(e))
                
    def isConnectionReady(self, host, port):
        """
        Checks wether a connection is ready or not.
        Args:
            port: the port assigned to the connection.
        Returns:
            True if the connection is ready or False otherwise.
        Raises:
            NetworkManagerException: a NetworkManagerException will be raised if 
                - there were errors while establishing the connection, or 
                - the connection was abnormally closed, or
                - the supplied port is free
        """
        if not self.__connectionPool.has_key((host,port)) :
            raise NetworkManagerException("The port " + str(port) +" is not in use") 
        connection = self.__connectionPool[(host, port)]
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
            self.__connectionPool.pop((connection.getIPAddress(), connection.getPort()))
            raise NetworkManagerException("Error: " + str(connection.getError()))
        if (connection.wasUnexpectedlyClosed()):
            self.__connectionPool.pop((connection.getIPAddress(), connection.getPort()))
            raise NetworkManagerException("Error: " + "The connection was closed abnormally")
        
    def sendPacket(self, host, port, packet):
        """
        Sends a packet through the specified port and IP address.
        Args:
            port: The port assigned to the connection that will be used to send the packet.
            packet: The packet to send.
        Returns:
            Nothing
        Raises:
            NetworkManagerException: a NetworkManagerException will be raised if 
            - the connection is a server connection and it's not ready yet, or
            - the connection doesn't exist
        @attention: If the connection is not ready, the packet will be discarded.
        To avoid this, you must check the connection's availability BEFORE using it.
        """
        if not self.__connectionPool.has_key((host, port)) :
            raise NetworkManagerException("There's nothing attached to the port " + str(port))
        connection = self.__connectionPool[(host, port)]
        if connection.isReady() :
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
        
    def closeConnection(self, host, port):
        """
        Closes a connection
        Args:
            port: The port assigned to the connection. If it's free, a NetworkManagerException will be
            raised.
        Returns:
            Nothing
        """
        if not self.__connectionPool.has_key((host, port)) :
            raise NetworkManagerException("There's nothing attached to the port " + str(port))
        # Retrieve the connection
        connection = self.__connectionPool[(host, port)]     
        # Ask the connection to close
        connection.close()