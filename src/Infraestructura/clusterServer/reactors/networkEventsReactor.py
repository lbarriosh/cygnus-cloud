# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: networkEventsReactor.py    
    Version: 5.0
    Description: network events reactor definition
    
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

from clusterServer.database.server_state_t import SERVER_STATE_T
from network.twistedInteraction.clientConnection import RECONNECTION_T

class NetworkEventsReactor(object):
    """
    These objects process the network events
    """    
    
    def __init__(self, dbConnector, repositoryIP, repositoryPort):
        """
        Initializes the reactor's state
        Args:
            dbConnector: a database connnector
            repositoryIP: the image repository's IP
            repositoryPort: the image repository's port
        """
        self.__dbConnector = dbConnector    
        self.__repositoryIP = repositoryIP
        self.__repositoryPort = repositoryPort
    
    def processVMServerReconnectionData(self, ipAddress, reconnection_status) :
        """
        Processes a virtual machine server reconnection event
        Args:
            ipAddress: a virutal machine server's IP address
            port: the virtual machine server's control connection port
            reconnection_status: the reconnection process status
        Returns:
            Nothing
        """
        if (reconnection_status == RECONNECTION_T.RECONNECTING) : 
            status = SERVER_STATE_T.RECONNECTING
        elif (reconnection_status == RECONNECTION_T.REESTABLISHED) :
            status = SERVER_STATE_T.READY
        else :
            status = SERVER_STATE_T.CONNECTION_TIMED_OUT
        
        serverID = self.__dbConnector.getVMServerID(ipAddress)
        self.__dbConnector.updateVMServerStatus(serverID, status)
        
    def processImageRepositoryReconnectionData(self, reconnection_status):
        """
        Processes an image repository reconnection event
        Args:
            reconnection_status: the reconnection process status
        Returns:
            Nothing
        """
        if (reconnection_status == RECONNECTION_T.RECONNECTING) : 
            status = SERVER_STATE_T.RECONNECTING
        elif (reconnection_status == RECONNECTION_T.REESTABLISHED) :
            status = SERVER_STATE_T.READY
        else :
            status = SERVER_STATE_T.CONNECTION_TIMED_OUT
        self.__dbConnector.updateImageRepositoryConnectionStatus(self.__repositoryIP, self.__repositoryPort, status)