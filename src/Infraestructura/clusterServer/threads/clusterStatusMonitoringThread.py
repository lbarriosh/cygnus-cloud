# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: clusterStatusMonitoringThread.py    
    Version: 3.0
    Description: cluster status update thread definitions
    
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
from ccutils.threads.basicThread import BasicThread
from network.manager.networkManager import NetworkManager
from virtualMachineServer.packetHandling.packet_t import VM_SERVER_PACKET_T as VMSRVR_PACKET_T

from time import sleep

class ClusterStatusMonitoringThread(BasicThread):
    """
    This threads will periodically send the status request packets to to the cluster's machines.
    """
    def __init__(self, sleepTime, dbConnector, networkManager, repositoryIP, repositoryPort,
                 vmServerPacketHandler, imageRepositoryPacketHandler):
        """
        Initializes the thread's state
        Args:
            sleepTime: the sleep time between updates (in seconds)
            dbConnector: a cluster server database connector
            networkManager: the NetworkManager object to use
            repositoryIP: the image repository's IP address
            repositoryPort: the image repository's port
            vmServerPacketHandler: the virtual machine server packet handler
            imageRepositoryPacketHandler: the image repository packet handler
        """
        BasicThread.__init__(self, "Cluster status update thread")
        self.__sleepTime = sleepTime
        self.__commandsDBConnector = dbConnector
        self.__networkManager = networkManager
        self.__vmServerPacketHandler = vmServerPacketHandler
        self.__imageRepositoryPacketHandler = imageRepositoryPacketHandler
        self.__repositoryIP = repositoryIP
        self.__repositoryPort = repositoryPort
        
    def run(self):
        while not self.finish() :
            self.__sendStatusRequestPacketsToClusterMachines()
            sleep(self.__sleepTime)

    def __sendStatusRequestPacketsToClusterMachines(self):
        """
        Sends the status request packets to the cluster machines.
        Args:
            None
        Returns:
            Nothing
        """
        for serverID in self.__commandsDBConnector.getVMServerIDs() :
            serverData = self.__commandsDBConnector.getVMServerConfiguration(serverID)
            if (serverData["ServerStatus"] != SERVER_STATE_T.SHUT_DOWN and serverData["ServerStatus"] != SERVER_STATE_T.CONNECTION_TIMED_OUT
                and serverData["ServerStatus"] != SERVER_STATE_T.RECONNECTING) :
                self.__sendStatusRequestToVMServer(serverData["ServerIP"], serverData["ServerPort"])
        p = self.__imageRepositoryPacketHandler.createStatusRequestPacket()
        self.__networkManager.sendPacket(self.__repositoryIP, self.__repositoryPort, p) 
        
    def __sendStatusRequestToVMServer(self, vmServerIP, vmServerPort):
        """
        Sends a status request packet to a virtual machine server
        Args:
            vmServerIP : the virtual machine server's IP address
            vmServerPort: the virtual machine server control connection's port
        Returns:
            Nothing
        """
        p = self.__vmServerPacketHandler.createVMServerDataRequestPacket(VMSRVR_PACKET_T.SERVER_STATUS_REQUEST)
        errorMessage = self.__networkManager.sendPacket(vmServerIP, vmServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(vmServerIP, vmServerPort, "status request", errorMessage)
        p = self.__vmServerPacketHandler.createVMServerDataRequestPacket(VMSRVR_PACKET_T.QUERY_ACTIVE_DOMAIN_UIDS)            
        errorMessage = self.__networkManager.sendPacket(vmServerIP, vmServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(vmServerIP, vmServerPort, "active domain UIDs request", errorMessage)