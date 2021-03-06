# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: clusterEndpointCallback.py    
    Version: 2.0
    Description: cluster endpoint packet callback
    
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

class ClusterEndpointCallback(NetworkCallback):
    '''
    These objects will be used to process the packets sent from the cluster endpoint.
    '''
    def __init__(self, packetReactor):
        """
        Initializes the callback's state
        Args:
            packetReactor: the object that will process all the incoming packets
                sent from the cluster endpoint.
        """
        self.__packetReactor = packetReactor
        
    def processPacket(self, packet):
        """
        Processes an incoming packet sent from the cluster endpoint.
        Args:
            packet:
                The packet to process
        Returns:
            Nothing
        """
        self.__packetReactor.processClusterEndpointIncomingPacket(packet)