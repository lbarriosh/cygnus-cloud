# -*- coding: utf8 -*-
'''
Created on May 10, 2013

@author: luis
'''

from virtualMachineServer.packetHandling.packet_t import VM_SERVER_PACKET_T as VMSRVR_PACKET_T
from clusterServer.packetHandling.packet_t import CLUSTER_SERVER_PACKET_T as ENDPOINT_PACKET_T
from clusterServer.database.server_state_t import SERVER_STATE_T
from clusterServer.database.image_state_t import IMAGE_STATE_T
from time import sleep
from errors.codes import ERROR_DESC_T

class VMServerPacketReactor(object):
    
    def __init__(self, dbConnector, networkManager, listenningPort, vmServerPacketHandler, webPacketHandler):
        self.__dbConnector = dbConnector        
        self.__networkManager = networkManager
        self.__listenningPort = listenningPort
        self.__vmServerPacketHandler = vmServerPacketHandler
        self.__webPacketHandler = webPacketHandler
    
    def processVMServerIncomingPacket(self, packet):
        """
        Procesa un paquete enviado desde un servidor de máquinas virtuales
        Argumentos:
            packet: el paquete a procesar
        Devuelve:
            Nada
        """
        data = self.__vmServerPacketHandler.readPacket(packet)
        if (data["packet_type"] == VMSRVR_PACKET_T.SERVER_STATUS) :
            self.__updateVMServerStatus(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.DOMAIN_CONNECTION_DATA) :
            self.__sendVMConnectionData(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.ACTIVE_VM_DATA) :
            self.__sendDomainsVNCConnectionData(packet)
        elif (data["packet_type"] == VMSRVR_PACKET_T.ACTIVE_DOMAIN_UIDS) :
            self.__processActiveDomainUIDs(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.IMAGE_DEPLOYMENT_ERROR or data["packet_type"] == VMSRVR_PACKET_T.IMAGE_DELETION_ERROR):
            self.__processImageDeploymentErrorPacket(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.IMAGE_DEPLOYED or data["packet_type"] == VMSRVR_PACKET_T.IMAGE_DELETED):
            self.__processImageDeploymentPacket(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.IMAGE_EDITED):
            self.__processImageEditedPacket(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.IMAGE_EDITION_ERROR):
            self.__processImageEditionError(data)
        elif (data["packet_type"] == VMSRVR_PACKET_T.INTERNAL_ERROR) :
            self.__processVMServerInternalError(data)
            
    def __updateVMServerStatus(self, data):
        """
        Procesa un paquete de estado enviado desde un servidor de máquinas virtuales
        Argumentos:
            data: diccionario con los datos del paquete recibido
        Devuelve:
            Nada
        """
        # Identificar el servidor de máquinas virtuales y actualizar su estado en la base de datos.
        
        serverID = None
        while (serverID == None) :
            serverID = self.__dbConnector.getVMServerID(data["VMServerIP"])
            if (serverID == None) :
                sleep(0.1)
                
        self.__dbConnector.updateVMServerStatus(serverID, SERVER_STATE_T.READY)
        self.__dbConnector.setVMServerStatistics(serverID, data["ActiveDomains"], data["RAMInUse"], data["RAMSize"], 
                                                 data["FreeStorageSpace"], data["AvailableStorageSpace"], data["FreeTemporarySpace"],
                                                 data["AvailableTemporarySpace"], data["ActiveVCPUs"], data["PhysicalCPUs"])
            
    def __processVMServerInternalError(self, data):
        # Liberar los recursos asignados
        self.__dbConnector.freeVMServerResources(data["CommandID"], True)
        # Generar un paquete de error
        p = self.__webPacketHandler.createErrorPacket(ENDPOINT_PACKET_T.VM_SERVER_INTERNAL_ERROR, ERROR_DESC_T.VMSRVR_INTERNAL_ERROR, data["CommandID"])
        self.__networkManager.sendPacket('', self.__listenningPort, p)
        
    def __processImageEditedPacket(self, data):
        # Actualizar la base de datos
        self.__dbConnector.deleteActiveVMLocation(data["CommandID"])
        if (not self.__dbConnector.isImageEditionCommand(data["CommandID"])) :            
            familyID = self.__dbConnector.getNewVMVanillaImageFamily(data["CommandID"])
            self.__dbConnector.deleteNewVMVanillaImageFamily(data["CommandID"])
            self.__dbConnector.registerFamilyID(data["ImageID"], familyID)                
            # Enviar la respuesta
            p = self.__webPacketHandler.createImageEditedPacket(data["CommandID"], data["ImageID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)
        else :
            self.__dbConnector.removeImageEditionCommand(data["CommandID"])
            # Evitar que todas las copias de la imagen puedan arrancarse
            self.__dbConnector.changeImageStatus(data["ImageID"], IMAGE_STATE_T.EDITED)  
            p = self.__webPacketHandler.createCommandExecutedPacket(data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)   
        
        # Liberar los recursos asignados a la máquina
        self.__dbConnector.freeVMServerResources(data["CommandID"], False)        
        self.__dbConnector.freeImageRepositoryResources(data["CommandID"], False) 
    
    def __processImageEditionError(self, data):
        
        # Actualizar la base de datos        
        if (not self.__dbConnector.isImageEditionCommand(data["CommandID"])) :        
            self.__dbConnector.deleteNewVMVanillaImageFamily(data["CommandID"])
            packet_type = ENDPOINT_PACKET_T.IMAGE_CREATION_ERROR
        else :
            self.__dbConnector.removeImageEditionCommand(data["CommandID"])
            packet_type = ENDPOINT_PACKET_T.IMAGE_EDITION_ERROR        
        # Enviar la respuesta
        p = self.__webPacketHandler.createErrorPacket(packet_type, data["ErrorDescription"], data["CommandID"])
        self.__networkManager.sendPacket('', self.__listenningPort, p)
        
        # Liberar los recursos asignados a la máquina
        self.__dbConnector.freeVMServerResources(data["CommandID"], True)
        self.__dbConnector.freeImageRepositoryResources(data["CommandID"], True)
            
    def __processImageDeploymentErrorPacket(self, data):
        if (self.__dbConnector.isImageEditionCommand(data["CommandID"])) :
            packet_type = ENDPOINT_PACKET_T.IMAGE_EDITION_ERROR
            self.__dbConnector.removeImageEditionCommand(data["CommandID"])
            
        elif (self.__dbConnector.isAutoDeploymentCommand(data["CommandID"])) :
            (generateOutput, _unused) = self.__dbConnector.handleAutoDeploymentCommandOutput(data["CommandID"], True)
            if (generateOutput) :              
                p = self.__webPacketHandler.createErrorPacket(ENDPOINT_PACKET_T.AUTO_DEPLOY_ERROR, ERROR_DESC_T.CLSRVR_AUTOD_ERROR, data["CommandID"])
                self.__networkManager.sendPacket('', self.__listenningPort, p)
                
        elif (data["packet_type"] == VMSRVR_PACKET_T.IMAGE_DEPLOYMENT_ERROR) :
            packet_type = ENDPOINT_PACKET_T.IMAGE_DEPLOYMENT_ERROR
        else :
            packet_type = ENDPOINT_PACKET_T.DELETE_IMAGE_FROM_SERVER_ERROR
            
        p = self.__webPacketHandler.createErrorPacket(packet_type, data["ErrorCode"], data["CommandID"])
        self.__networkManager.sendPacket('', self.__listenningPort, p)
        
        # Liberar los recursos asignados a la máquina
        self.__dbConnector.freeVMServerResources(data["CommandID"], True)
        
    def __processImageDeploymentPacket(self, data):
        # Liberar los recursos asignados a la imagen (si existen)
        self.__dbConnector.freeVMServerResources(data["CommandID"], False)
        
        serverID = self.__dbConnector.getVMServerID(data["SenderIP"])
        if (self.__dbConnector.isImageEditionCommand(data["CommandID"])) :                  
            # Marcar la imagen como lista
            self.__dbConnector.changeImageCopyStatus(data["ImageID"], serverID, IMAGE_STATE_T.READY)
            # Si no hay más copias sucias, el comando de edición habrá terminado
            if (not self.__dbConnector.isThereSomeImageCopyInState(data["ImageID"], IMAGE_STATE_T.DEPLOY)) :
                p = self.__webPacketHandler.createCommandExecutedPacket(data["CommandID"])
                self.__networkManager.sendPacket('', self.__listenningPort, p)
                self.__dbConnector.removeImageEditionCommand(data["CommandID"])
        elif (self.__dbConnector.isImageDeletionCommand(data["CommandID"])) :
            # Borrar la ubicación de la imagen de la base de datos
            self.__dbConnector.deleteImageFromServer(serverID, data["ImageID"])
            # Si no hay más copias que eliminar, el comando de edición habrá terminado
            if (not self.__dbConnector.isThereSomeImageCopyInState(data["ImageID"], IMAGE_STATE_T.DELETE)) :
                p = self.__webPacketHandler.createCommandExecutedPacket(data["CommandID"])
                self.__networkManager.sendPacket('', self.__listenningPort, p)
                self.__dbConnector.removeImageDeletionCommand(data["CommandID"])
        elif (self.__dbConnector.isAutoDeploymentCommand(data["CommandID"])) :
            (generateOutput, error) = self.__dbConnector.handleAutoDeploymentCommandOutput(data["CommandID"], False)
            if (not error) :
                self.__dbConnector.assignImageToServer(serverID, data["ImageID"])
            if (generateOutput) :
                if (error) :
                    p = self.__webPacketHandler.createErrorPacket(ENDPOINT_PACKET_T.AUTO_DEPLOY_ERROR, ERROR_DESC_T.CLSRVR_AUTOD_ERROR, data["CommandID"])
                else :
                    p = self.__webPacketHandler.createCommandExecutedPacket(data["CommandID"])                
                self.__networkManager.sendPacket('', self.__listenningPort, p)
        else :
            if (data["packet_type"] == VMSRVR_PACKET_T.IMAGE_DEPLOYED) :
                self.__dbConnector.assignImageToServer(serverID, data["ImageID"])                
            else :
                self.__dbConnector.deleteImageFromServer(serverID, data["ImageID"])
            p = self.__webPacketHandler.createCommandExecutedPacket(data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)
            
    def __sendVMBootError(self, data):
        self.__dbConnector.removeVMBootCommand(data["CommandID"])
        commandData = self.__dbConnector.getVMBootCommandData(data["CommandID"])
        self.__dbConnector.removeVMBootCommand(data["CommandID"])
        self.__dbConnector.deleteActiveVMLocation(commandData[0])
        p = self.__webPacketHandler.createErrorPacket(ENDPOINT_PACKET_T.VM_BOOT_FAILURE, ERROR_DESC_T.VMSRVR_INTERNAL_ERROR, commandData[0])
        self.__networkManager.sendPacket('', self.__listenningPort, p)
        
    def __sendVMConnectionData(self, data):
        """
        Envía al endpoint los datos de conexión VNC a UNA máquina
        virtual que se acaba de crear.
        Argumetnos:
            data: diccionario con los datos del paquete
        Devuelve:
            Nada
        """
        # El comando ya se ha ejecutado. No tenemos que seguir controlando el tiempo que tarda.
        self.__dbConnector.removeVMBootCommand(data["CommandID"])
        
        p = self.__webPacketHandler.createVMConnectionDataPacket(data["VNCServerIP"], 
                                                                 data["VNCServerPort"], data["VNCServerPassword"], data["CommandID"])
        self.__networkManager.sendPacket('', self.__listenningPort, p)      
        # Preparar la "liberación" de los recursos asignados a la máquina.
        self.__dbConnector.freeVMServerResources(data["CommandID"], False)
        
    def __processActiveDomainUIDs(self, data):
        vmServerID = self.__dbConnector.getVMServerID(data["VMServerIP"])
        self.__dbConnector.registerHostedVMs(vmServerID, data["Domain_UIDs"])
        
    def __sendDomainsVNCConnectionData(self, packet):
        """
        Envía al endpoint los datos de conexión VNC de todas las máquinas
        virtuales activas del servidor de máquinas virtuales
        Argumentos:
            packet: diccionario con los datos a procesar
        Devuelve:
            Nada
        """
        p = self.__webPacketHandler.createActiveVMsDataPacket(packet)
        self.__networkManager.sendPacket('', self.__listenningPort, p)