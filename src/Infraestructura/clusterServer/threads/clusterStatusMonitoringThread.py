# -*- coding: utf8 -*-
'''
Created on Apr 11, 2013

@author: luis
'''
from clusterServer.database.server_state_t import SERVER_STATE_T
from ccutils.threads.basicThread import BasicThread
from network.manager.networkManager import NetworkManager
from virtualMachineServer.packetHandling.packet_t import VM_SERVER_PACKET_T as VMSRVR_PACKET_T

from time import sleep

class ClusterStatusMonitoringThread(BasicThread):
    
    def __init__(self, sleepTime, dbConnector, networkManager, repositoryIP, repositoryPort,
                 vmServerPacketHandler, imageRepositoryPacketHandler):
        BasicThread.__init__(self, "Cluster status update thread")
        self.__sleepTime = sleepTime
        self.__dbConnector = dbConnector
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
        for serverID in self.__dbConnector.getVMServerIDs() :
            serverData = self.__dbConnector.getVMServerBasicData(serverID)
            if (serverData["ServerStatus"] != SERVER_STATE_T.SHUT_DOWN and serverData["ServerStatus"] != SERVER_STATE_T.CONNECTION_TIMED_OUT) :
                self.__sendStatusRequestToVMServer(serverData["ServerIP"], serverData["ServerPort"])
        p = self.__imageRepositoryPacketHandler.createStatusRequestPacket()
        self.__networkManager.sendPacket(self.__repositoryIP, self.__repositoryPort, p) 
        
    def __sendStatusRequestToVMServer(self, vmServerIP, vmServerPort):
        """
        Envía los paquetes de solicitud de estado a un servidor de máquinas virtuales
        Argumentos:
            vmServerIP : la IP del servidor de máquinas virtuales
            vmServerPort: el puerto del servidor de máquinas virtuales
        Devuelve:
            Nada
        """
        p = self.__vmServerPacketHandler.createVMServerDataRequestPacket(VMSRVR_PACKET_T.SERVER_STATUS_REQUEST)
        errorMessage = self.__networkManager.sendPacket(vmServerIP, vmServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(vmServerIP, vmServerPort, "status request", errorMessage)
        p = self.__vmServerPacketHandler.createVMServerDataRequestPacket(VMSRVR_PACKET_T.QUERY_ACTIVE_DOMAIN_UIDS)            
        errorMessage = self.__networkManager.sendPacket(vmServerIP, vmServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(vmServerIP, vmServerPort, "active domain UIDs request", errorMessage)