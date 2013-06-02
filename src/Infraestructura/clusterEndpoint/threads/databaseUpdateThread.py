# -*- coding: utf8 -*-
'''
Definiciones del hilo de actualización periódica de la base de datos de estado
@author: Luis Barrios Hernández
@version: 1.1
'''

from ccutils.threads.basicThread import BasicThread
from network.manager.networkManager import NetworkManager
from clusterServer.packetHandling.packet_t import CLUSTER_SERVER_PACKET_T as PACKET_T
from time import sleep

class VMServerMonitoringThread(BasicThread):
    """
    Estos hilos refrescan la base de datos de estado periódicamente.
    """
    def __init__(self, webPacketHandler, networkManager, commandsProcessor, clusterServerIP, clusterServerPort, sleepTime):
        """
        Inicializa el estado
        Argumentos:
            updateHandler: el objeto que envía los paquetes para obtener la información
            sleepTime: tiempo (en segundos) que separa dos actualizaciones consecutivas.
        """
        BasicThread.__init__(self, "Status database update thread")
        self.__packetHandler = webPacketHandler
        self.__networkManager = networkManager
        self.__commandsProcessor = commandsProcessor
        self.__clusterServerIP = clusterServerIP
        self.__clusterServerPort = clusterServerPort
        self.__sleepTime = sleepTime
        
    def run(self):
        """
        Envía los paquetes de actualización del estado
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        while not self.finish() :
            self.__sendUpdateRequestPackets()
            sleep(self.__sleepTime)
            
    def __sendUpdateRequestPackets(self):
        """
        Solicita información de estado al serividor de cluster
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        if (self.__commandsProcessor.finish()) :
            return
        # Enviamos paquetes para obtener los tres tipos de información que necesitamos para actualizar la base de datos de estado
        p = self.__packetHandler.createDataRequestPacket(PACKET_T.QUERY_VM_SERVERS_STATUS)
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)          
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Virtual machine servers status", errorMessage)     
        
        p = self.__packetHandler.createDataRequestPacket(PACKET_T.QUERY_VM_DISTRIBUTION)
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)        
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Virtual machine distribution", errorMessage)
        
        p = self.__packetHandler.createDataRequestPacket(PACKET_T.QUERY_ACTIVE_VM_DATA)
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Active virtual machines data", errorMessage)
        
        p = self.__packetHandler.createDataRequestPacket(PACKET_T.QUERY_REPOSITORY_STATUS)
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Image repository status", errorMessage)
        
        p = self.__packetHandler.createDataRequestPacket(PACKET_T.QUERY_VM_SERVERS_RESOURCE_USAGE)
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Virtual machine servers resource usage", errorMessage)