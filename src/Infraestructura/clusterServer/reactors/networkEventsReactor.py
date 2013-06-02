# -*- coding: utf8 -*-

from clusterServer.database.server_state_t import SERVER_STATE_T
from network.twistedInteraction.clientConnection import RECONNECTION_T

class NetworkEventsReactor(object):
    
    def __init__(self, dbConnector, repositoryIP, repositoryPort):
        self.__dbConnector = dbConnector    
        self.__repositoryIP = repositoryIP
        self.__repositoryPort = repositoryPort
    
    def processVMServerReconnectionData(self, ipAddress, reconnection_status) :
        """
        Procesa una reconexión con un servidor de máquinas virtuales
        Argumentos:
            ipAddress: la dirección IP del servidor de máquinas virtuales
            port: el puerto en el que el servidor de máquinas virtuales está escuchando
            reconnection_status: el estado del proceso de reconexión
        Devuelve:
            Nada
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
        if (reconnection_status == RECONNECTION_T.RECONNECTING) : 
            status = SERVER_STATE_T.RECONNECTING
        elif (reconnection_status == RECONNECTION_T.REESTABLISHED) :
            status = SERVER_STATE_T.READY
        else :
            status = SERVER_STATE_T.CONNECTION_TIMED_OUT
        self.__dbConnector.updateImageRepositoryConnectionStatus(self.__repositoryIP, self.__repositoryPort, status)