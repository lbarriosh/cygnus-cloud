# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: databaseUpdateThread.py    
    Version: 2.0
    Description: cluster endpoint daemon database thread
    
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

from ccutils.threads.basicThread import BasicThread
from network.manager.networkManager import NetworkManager
from clusterServer.packetHandling.packet_t import CLUSTER_SERVER_PACKET_T as PACKET_T
from time import sleep

class VMServerMonitoringThread(BasicThread):
    """
    These threads send the update request packets to the cluster server.
    """
    def __init__(self, clusterServerPacketHandler, networkManager, commandsProcessor, clusterServerIP, clusterServerPort, sleepTime):
        """
        Initializes the thread's state
        Args:
            clusterServerPacketHandler: the cluster server packet handler to use
            networkManager: the NetworkManager object to use
            commandsProcessor: the commands processor object to use
            clusterServerIP: the cluster server's IP address
            clusterServerPort: the cluster server control connection's port
            sleepTime: the sleep time between two consecutive updates (in seconds)
        """
        BasicThread.__init__(self, "Status database update thread")
        self.__packetHandler = clusterServerPacketHandler
        self.__networkManager = networkManager
        self.__commandsProcessor = commandsProcessor
        self.__clusterServerIP = clusterServerIP
        self.__clusterServerPort = clusterServerPort
        self.__sleepTime = sleepTime
        
    def run(self):
        while not self.finish() :
            self.__sendUpdateRequestPackets()
            sleep(self.__sleepTime)
            
    def __sendUpdateRequestPackets(self):
        """
        Sends the update request packets to the cluster server
        Args:
            None
        Returns:
            Nothing
        """
        if (self.__commandsProcessor.finish()) :
            return
        p = self.__packetHandler.createDataRequestPacket(PACKET_T.QUERY_VM_SERVERS_STATUS)
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)          
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Virtual machine servers status", errorMessage)     
        
        p = self.__packetHandler.createDataRequestPacket(PACKET_T.QUERY_VM_DISTRIBUTION)
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)        
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Virtual machine distribution", errorMessage)
        
        p = self.__packetHandler.createDataRequestPacket(PACKET_T.QUERY_ACTIVE_VM_VNC_DATA)
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Active virtual machines data", errorMessage)
        
        p = self.__packetHandler.createDataRequestPacket(PACKET_T.QUERY_REPOSITORY_STATUS)
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Image repository status", errorMessage)
        
        p = self.__packetHandler.createDataRequestPacket(PACKET_T.QUERY_VM_SERVERS_RESOURCE_USAGE)
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Virtual machine servers resource usage", errorMessage)