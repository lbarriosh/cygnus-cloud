# -*- coding: utf8 -*-
'''
In this module we define the NetworkManager class and its main dependencies.
@author: Luis Barrios Hernández
@version: 1.0
'''

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint
from twisted.internet.protocol import Protocol, Factory
from threading import Thread
from utils.multithreadingPriorityQueue import GenericThreadSafePriorityQueue
from network.packets.packet import Packet, Packet_TYPE
from network.exceptions.networkManager import NetworkManagerException
from time import sleep

class _CygnusCloudProtocol(Protocol):
    """
    Network protocol implementation
    """
    def __init__(self, queue):
        """
        Initializes the protocol with an incoming data priority queue.
        """
        self.__incomingPacketsQueue = queue
    
    def dataReceived(self, data):
        """
        Generates a packet with the received data and stores it on the
        incoming priority queue associated with the protocol instance.
        """
        p = Packet._deserialize(data)
        self.__incomingPacketsQueue.queue(p.getPriority(), p)
    
    def connectionMade(self):
        print "Connection established"
    
    def connectionLost(self, reason):
        print "Connection lost"  
    
    def sendData(self, packet):
        """
        Sends the serialized packet
        """
        self.transport.write(packet._serialize())
        
    def disconnect(self):
        """
        Closes the connection
        """
        self.transport.loseConnection()
        
class _CygnusCloudProtocolFactory(Factory):
    """
    Protocol factory. These objects are used to create protocol instances
    within the Twisted Framework.
    """    
    def __init__(self, queue):
        self.protocol = _CygnusCloudProtocol
        self.__queue = queue        
        self.__instance = None    
    
    def buildProtocol(self, addr):
        """
        Builds a protocol, stores a pointer to it and finally returns it.
        This method is called inside Twisted code.
        """
        self.__instance = _CygnusCloudProtocol(self.__queue)        
        return self.__instance

    def getInstance(self):
        """
        Returns the last built instance
        """
        return self.__instance
    
    def getIncomingDataQueue(self):
        """
        Returns the incoming packages queue
        """
        return self.__queue
        
class _TwistedReactorThread(Thread):
    """
    These threads run the twisted reactor loop.
    @attention: Once the reactor is stopped, it won\'t be able to start again.
    """
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):        
        reactor.run(installSignalHandlers=0)
        
    def stop(self):
        reactor.stop()
        
class NetworkCallback(object):
    """
    A class that represents a network callback object.
    These objects will process the incoming packages.
    """
    def processPacket(self, packet):
        raise NotImplementedError
    
class _IncomingDataThread(Thread):
    """
    A class associated to the incoming packages threads.
    This threads will process the incoming packages.
    """
    def __init__(self, queue, callbackObject):
        """
        Initializes the thread's state
        """
        Thread.__init__(self)
        self.__stop = False
        self.__queue = queue
        self.__isRunning = False
        self.__callbackObject = callbackObject
        
    def start(self):
        if not self.__isRunning :
            Thread.start(self)
            self.__isRunning = True
    
    def stop(self):
        self.__stop = True
        
    def run(self):
        while not (self.__stop and self.__queue.isEmpty()):
            while not self.__queue.isEmpty() :
                packet = self.__queue.dequeue()
                self.__callbackObject.processPacket(packet)
            if not self.__stop :
                sleep(10) # Sleep for 10 milliseconds when there's nothing to do   
    
        
class NetworkManager():
    """
    This class provides a facade to use Twisted in a higher abstraction level way. 
    @attention: Due to some Twisted related limitations, do NOT stop the network service 
    UNTIL you KNOW PERFECTLY WELL that you won\'t be using it again. 
    """
    def __init__(self):
        """
        Initializes the state
        """
        self.__connectionPool = dict();
        self.__networkThread = _TwistedReactorThread()
        
    def startNetworkService(self):
        """
        Starts the reactor thread
        """
        self.__networkThread.start()
        
    def stopNetworkService(self):
        """
        Stops the reactor thread.
        @attention: Due to some Twisted related limitations, do NOT stop the network service 
        UNTIL you KNOW PERFECTLY WELL that you won\'t be using it again. 
        """
        for (_protocol, _queue, thread, _callback) in self.__connectionPool.values() :
            thread.stop()
            thread.join()
        self.__networkThread.stop()
        self.__networkThread.join()
        
    def __allocateConnectionResources(self, callbackObject):
        """
        Allocates (if necessary) the resources associated to a new connection 
        """
        queue = None
        thread = None
        callback = None
        found = False
        for (_protocol, queue, thread, callback) in self.__connectionPool.values() :
            if (callback == callbackObject) :
                # Everything is allocated. Let's reuse it.
                found = True
                break
        if found :
            return (queue, thread)
        else :
            queue = GenericThreadSafePriorityQueue()
            thread = _IncomingDataThread(queue, callbackObject)
            return (queue, thread)
        
    def connectTo(self, host, port, timeout, callbackObject):
        """
        Connects to a remote server using its arguments
        """
        if self.__connectionPool.has_key(port) :
            raise NetworkManagerException("The port " + str(port) +" is already in use")
        # The port is free => proceed
        # Allocate the connection resources
        (queue, thread) = self.__allocateConnectionResources(callbackObject)       
        # Create and configure the endpoint
        factory = _CygnusCloudProtocolFactory(queue)
        endpoint = TCP4ClientEndpoint(reactor, host, port, timeout, None)
        endpoint.connect(factory)   
        time = 0
        while factory.getInstance() is None and time <= timeout:            
            sleep(1)
            time += 1
        if factory.getInstance() is None :
            raise NetworkManagerException("The host " + host + ":" + str(port) +" seems to be unreachable")
        # Add the new connection to the connection pool
        self.__connectionPool[port] = (factory.getInstance(), queue, callbackObject, thread) 
        # Start the thread
        thread.start()
        
    def listenIn(self, port, callbackObject):
        """
        Creates a server using its arguments
        """   
        if self.__connectionPool.has_key(port) :
            raise NetworkManagerException("The port " + str(port) +" is already in use") 
        # The port is free => proceed
        # Allocate the connection resources
        (queue, thread) = self.__allocateConnectionResources(callbackObject)       
        # Create and configure the endpoint
        endpoint = TCP4ServerEndpoint(reactor, port)
        factory = _CygnusCloudProtocolFactory(queue)
        endpoint.listen(factory)
        while factory.getInstance() is None :            
            sleep(1)
        # Add the new connection to the connection pool
        self.__connectionPool[port] = (factory.getInstance(), queue, callbackObject, thread) 
        # Start the thread
        thread.start()
        
    def sendPacket(self, port, packet):
        """
        Sends a packet through the specified port
        """
        if not self.__connectionPool.has_key(port) :
            raise NetworkManagerException("There's nothing attached to the port " + str(port))
        (protocol, _queue, _thread, _callback) = self.__connectionPool[port]
        protocol.sendData(packet)
        
    def createPacket(self, priority):
        """
        Creates an empty data packet and returns it
        """
        if not isinstance(priority, int) or  priority < 0 :
            raise NetworkManagerException("Data packets\' priorities MUST be positive integers")
        p = Packet(Packet_TYPE.DATA, priority)
        return p
        
    def closeConnection(self, port):
        """
        Closes a connection
        """
        if not self.__connectionPool.has_key(port) :
            raise NetworkManagerException("There's nothing attached to the port " + str(port))
        (protocol, _queue, callbackObject, thread) = self.__connectionPool[port]
        protocol.disconnect()
        # Delete the mapping
        self.__connectionPool.pop(port)
        stopThread = True
        for (_protocol, _queue, _thread, callback) in self.__connectionPool.values() :
            if (callbackObject == callback) :
                # The thread is assigned to another connection => we won't stop it now
                stopThread = False
                break
        if stopThread :
            thread.stop()