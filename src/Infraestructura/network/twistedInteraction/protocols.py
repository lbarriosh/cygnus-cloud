# -*- coding: UTF8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: protocols.py    
    Version: 5.0
    Description: CygnusCloud protocol and protocol factory definitions
    
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

from twisted.protocols.basic import LineReceiver
from twisted.internet.protocol import Factory
from network.packets.packet import _Packet
from ccutils.dataStructures.multithreadingDictionary import GenericThreadSafeDictionary
from time import sleep

class CygnusCloudProtocol(LineReceiver):
    """
    CygnusCloud network protocol
    """
    def __init__(self, factory):
        """
        Initializes the protocol with the factory that created it.
        Args:
            factory: the protocol factory that created this protocol instance
        """       
        self.__factory = factory
        self.__disconnected = False
    
    def lineReceived(self, data):
        """
        Tells the protocol factory to process the received data.
        Args:
            data: The received data string
        Returns:
            Nothing
        Raises:
            PacketException: this exception will be raised when the received packet header
                is corrupt.
        """
        peerAddr = self.transport.getPeer()
        self.__factory.onPacketReceived(data, peerAddr.host, peerAddr.port)
    
    def connectionMade(self):
        """
        This method is called when a connection is established.
        Args:
            None
        Returns:
            Nothing
        """
        pass
    
    def connectionLost(self, reason):
        """
        This method is called when a connection is lost
        Args:
            reason: a message indicating why the connection was lost.
        Returns:
            Nothing
        """
        self.transport.abortConnection()
        self.__disconnected = True
        self.__factory.removeProtocol(self)
    
    def sendPacket(self, packet):
        """
        Sends the a packet to its destination.
        Args:
            packet: The packet to send
        Returns:
            Nothing
        """
        if (not self.__disconnected) :
            self.sendLine(packet._serialize())
        
    def disconnect(self):
        """
        Closes a CLIENT connection.
        Args:
            None
        Returns:
            Nothing
        """
        self.__disconnected = True
        self.transport.loseConnection()
        
class CygnusCloudProtocolFactory(Factory):
    """
    CygnusCloud protocol factory. These objects are used to create protocol instances
    within the Twisted Framework, and store all the data shared by multiple
    protocol instances.
    """    
    def __init__(self, transferQueue):
        """
        Initializes the protocol factory
        Args:
            transferQueue: the incoming data transferQueue to use by all protocol instances
        """
        self.protocol = CygnusCloudProtocol
        self._queue = transferQueue        
        self.__protocolPool = GenericThreadSafeDictionary()
    
    def buildProtocol(self, addr):
        """
        Builds a protocol, stores a pointer to it and finally returns it.
        This method is called inside Twisted code.
        """
        instance = CygnusCloudProtocol(self) 
        self.__protocolPool[(addr.host, addr.port)] = instance
        return instance   
        
    def removeProtocol(self, protocol):
        """
        Removes a protocol from the protocol pool
        """
        self.__protocolPool.removeElement(protocol)
        
    def isDisconnected(self):
        """
        Determines if there are active connections or not.
        """
        return self.__protocolPool.isEmpty()

    def sendPacket(self, packet, ip=None, port=None):
        """
        Returns the last built instance
        Args:
            None
        Returns:
            the last built protocol instance
        """
        if (ip == None) :
            for key in self.__protocolPool.keys():
                self.__protocolPool[key].sendPacket(packet)        
        else :
            self.__protocolPool[(ip, port)].sendPacket(packet)    
            
    def disconnect(self):
        """
        Asks Twisted to close the connection.
        Args:
            None
        Returns:
            Nothing
        """
        for key in self.__protocolPool.keys() :
            self.__protocolPool[key].disconnect()         
        
        while (not self.__protocolPool.isEmpty()) :
            sleep(0.1)
    
    def onPacketReceived(self, p, peerAddr, peerPort):
        """
        Returns the incoming packages queue
        Args:
            None
        Returns:
            The incoming packages queue
        """
        p = _Packet._deserialize(p)
        p._setSenderData(peerAddr, peerPort)
        self._queue.queue(p.getPriority(), p)