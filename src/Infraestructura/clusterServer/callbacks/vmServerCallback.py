# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: vmServerCallback.py    
    Version: 2.0
    Description: virtual machine server packet callback
    
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
from network.manager.networkManager import NetworkCallback
      
class VMServerCallback(NetworkCallback):
    '''
    These objects will be used to process the packets sent from a virtual machine server.
    '''
    def __init__(self, packetReactor, networkEventsReactor):
        """
        Initializes the callback's state
        Args:
            packetReactor: the object that will process all the incoming packets
                sent from a virtual machine server.
        """
        self.__packetReactor = packetReactor        
        self.__networkEventsReactor = networkEventsReactor
        
    def processPacket(self, packet):
        """
        Processes an incoming packet sent from a virtual machine server.
        Args:
            packet:
                The packet to process
        Returns:
            Nothing
        """        
        self.__packetReactor.processVMServerIncomingPacket(packet)   
        
    def processServerReconnectionData(self, ipAddress, port, reconnection_status):
        """
        Processes a reconnection status event
        Args:
            ipAddress: the connection's IPv4 address
            port: the connection's port
            reconnection_status: the reconnection process' status
        Returns:
            Nothing
        """
        self.__networkEventsReactor.processVMServerReconnectionData(ipAddress, reconnection_status)