# -*- coding: utf8 -*-
'''
Created on May 10, 2013

@author: luis
'''

from clusterServer.packetHandling.packet_t import CLUSTER_SERVER_PACKET_T as PACKET_T
from network.manager.networkManager import NetworkManager
from errors.codes import ERROR_DESC_T
from time import sleep
from clusterServer.loadBalancing.loadBalancer import MODE_T
from clusterServer.loadBalancing.penaltyBasedLoadBalancer import PenaltyBasedLoadBalancer
from clusterServer.database.server_state_t import SERVER_STATE_T
from clusterServer.database.image_state_t import IMAGE_STATE_T
from virtualMachineServer.packetHandling.packet_t import VM_SERVER_PACKET_T as VMSRVR_PACKET_T

class EndpointPacketReactor(object):
    
    def __init__(self, dbConnector, networkManager, vmServerPacketHandler, webPacketHandler, imageRepositoryPacketHandler,
                 vmServerCallback, listenningPort, repositoryIP, repositoryPort, loadBalancerSettings, 
                 averageCompressionRatio, useSSL):
        self.__dbConnector = dbConnector
        self.__networkManager = networkManager
        self.__vmServerPacketHandler = vmServerPacketHandler
        self.__packetHandler = webPacketHandler
        self.__imageRepositoryPacketHandler = imageRepositoryPacketHandler
        self.__loadBalancer = PenaltyBasedLoadBalancer(self.__dbConnector, loadBalancerSettings[1], 
            loadBalancerSettings[2], loadBalancerSettings[3], loadBalancerSettings[4], 
            loadBalancerSettings[5])
        self.__averageCompressionRatio = averageCompressionRatio
        self.__vmServerCallback = vmServerCallback
        self.__listenningPort = listenningPort
        self.__repositoryIP = repositoryIP
        self.__repositoryPort = repositoryPort
        self.__finished = False
        self.__useSSL = useSSL
    
    def processWebIncomingPacket(self, packet):
        """
        Procesa un paquete enviado desd el endpoint de la web
        Argumentos:
            packet: el paquete que hay que procesar
        Devuelve:
            Nada
        """
        data = self.__packetHandler.readPacket(packet)
        if (data["packet_type"] == PACKET_T.REGISTER_VM_SERVER) :
            self.__registerVMServer(data)
        elif (data["packet_type"] == PACKET_T.QUERY_VM_SERVERS_STATUS) :
            self.__sendStatusData(self.__dbConnector.getVMServerBasicData, self.__packetHandler.createVMServerStatusPacket)
        elif (data["packet_type"] == PACKET_T.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
            self.__unregisterOrShutdownVMServer(data)
        elif (data["packet_type"] == PACKET_T.BOOTUP_VM_SERVER) :
            self.__bootUpVMServer(data)
        elif (data["packet_type"] == PACKET_T.VM_BOOT_REQUEST):
            self.__bootUpVM(data)
        elif (data["packet_type"] == PACKET_T.HALT) :
            self.__doImmediateShutdown(data)
        elif (data["packet_type"] == PACKET_T.QUERY_VM_DISTRIBUTION) :
            self.__sendStatusData(self.__dbConnector.getHostedImages, self.__packetHandler.createVMDistributionPacket)
        elif (data["packet_type"] == PACKET_T.QUERY_ACTIVE_VM_DATA) :
            self.__requestVNCConnectionData()
        elif (data["packet_type"] == PACKET_T.DOMAIN_DESTRUCTION) :
            self.__destroyDomain(data)
        elif (data["packet_type"] == PACKET_T.VM_SERVER_CONFIGURATION_CHANGE):
            self.__changeVMServerConfiguration(data)
        elif (data["packet_type"] == PACKET_T.QUERY_REPOSITORY_STATUS):
            self.__sendRepositoryStatusData()
        elif (data["packet_type"] == PACKET_T.DEPLOY_IMAGE or data["packet_type"] == PACKET_T.DELETE_IMAGE_FROM_SERVER):
            self.__deployOrDeleteImage(data)
        elif (data["packet_type"] == PACKET_T.CREATE_IMAGE or data["packet_type"] == PACKET_T.EDIT_IMAGE):
            self.__createOrEditImage(data)
        elif (data["packet_type"] == PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE):
            self.__deleteImageFromInfrastructure(data)
        elif (data["packet_type"] == PACKET_T.AUTO_DEPLOY):
            self.__auto_deploy_image(data)
        elif (data["packet_type"] == PACKET_T.QUERY_VM_SERVERS_RESOURCE_USAGE):
            self.__sendStatusData(self.__dbConnector.getVMServerResouceUsage, self.__packetHandler.createVMServerResourceUsagePacket)
        
            
    def __registerVMServer(self, data):
        """
        Procesa un paquete de registro de un servidor de máquinas virtuales
        Argumentos:
            data: diccionario con los datos del paquete recibido
        Devuelve:
            Nada
        """
        try :
            # Comprobar si la IP y el nombre del servidor ya están en uso
            server_id = self.__dbConnector.getVMServerID(data["VMServerIP"])
            if (server_id != None) :
                raise Exception("The IP address " + data["VMServerIP"] + " is assigned to another VM server")
          
            server_id = self.__dbConnector.getVMServerID(data["VMServerName"])
            if (server_id != None) :
                raise Exception("The name " + data["VMServerName"] + " is assigned to another VM server")
            
            # Establecer la conexión
            self.__networkManager.connectTo(data["VMServerIP"], data["VMServerPort"], 
                                                20, self.__vmServerCallback, self.__useSSL, True)            
            while not self.__networkManager.isConnectionReady(data["VMServerIP"], data["VMServerPort"]) :
                sleep(0.1)
                
            # Registrar el nuevo servidor y pedirle su estado
            self.__dbConnector.registerVMServer(data["VMServerName"], data["VMServerIP"], 
                                                    data["VMServerPort"], data["IsVanillaServer"])            
            
            # Indicar al endpoint de la web que el comando se ha ejecutado con éxito
            p = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])
        except Exception:                
            p = self.__packetHandler.createErrorPacket(PACKET_T.VM_SERVER_REGISTRATION_ERROR,
                                                          ERROR_DESC_T.CLSRVR_VMSRVR_CONNECTION_ERROR, data["CommandID"])        
        self.__networkManager.sendPacket('', self.__listenningPort, p)
        
    def __bootUpVMServer(self, data):
        """
        Procesa un paquete de arranque de un servidor de máquinas virtuales
        Argumentos:
            data: diccionario con los datos del paquete recibido
        Devuelve:
            Nada
        """
        try :            
            # Comprobar si el servidor está registrado            
            serverNameOrIPAddress = data["ServerNameOrIPAddress"]
            serverId = self.__dbConnector.getVMServerID(serverNameOrIPAddress)
            if (serverId == None) :
                p = self.__packetHandler.createErrorPacket(PACKET_T.VM_SERVER_BOOTUP_ERROR, 
                                                              ERROR_DESC_T.CLSRVR_UNKNOWN_VMSRVR, data["CommandID"])
            else :
                serverData = self.__dbConnector.getVMServerBasicData(serverId)
                
                if (serverData["ServerStatus"] == SERVER_STATE_T.SHUT_DOWN or 
                    serverData["ServerStatus"] == SERVER_STATE_T.CONNECTION_TIMED_OUT) :                   
                
                    # Establecer la conexión            
                    self.__networkManager.connectTo(serverData["ServerIP"], serverData["ServerPort"], 
                                                        20, self.__vmServerCallback, self.__useSSL, True)
                    while not self.__networkManager.isConnectionReady(serverData["ServerIP"], serverData["ServerPort"]) :
                        sleep(0.1)
                        
                    # Solicitar el estado al servidor de máquinas virtuales            
                    self.__dbConnector.updateVMServerStatus(serverId, SERVER_STATE_T.BOOTING)       
                    
                    # Hacer que el servidor de máquinas virtuales sincronice sus imágenes con las del repositorio
                    imagesToDeploy = self.__dbConnector.getHostedImagesWithStatus(serverId, IMAGE_STATE_T.DEPLOY)
                    for imageID in imagesToDeploy :
                        familyID = self.__dbConnector.getFamilyID(imageID)
                        familyFeatures = self.__dbConnector.getVanillaImageFamilyFeatures(familyID)
                        p = self.__vmServerPacketHandler.createImageDeploymentPacket(self.__repositoryIP, self.__repositoryPort, imageID, 
                                                                                     self.__dbConnector.getImageEditionCommandID(imageID))
                        self.__dbConnector.allocateVMServerResources(data["CommandID"], serverId, 
                                                                 0, familyFeatures["osDiskSize"] + familyFeatures["dataDiskSize"], 
                                                                 0, 0, 1)
                        self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)
                        
                    imagesToDelete = self.__dbConnector.getHostedImagesWithStatus(serverId, IMAGE_STATE_T.DELETE)            
                    for imageID in imagesToDelete :
                        p = self.__vmServerPacketHandler.createDeleteImagePacket(imageID, self.__dbConnector.getImageDeletionCommandID(imageID))
                        self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)
                
                # Indicar al endpoint que el comando se ha ejecutado con éxito
                p = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])
        except Exception:
            p = self.__packetHandler.createErrorPacket(PACKET_T.VM_SERVER_BOOTUP_ERROR,
                                                          ERROR_DESC_T.CLSRVR_VMSRVR_CONNECTION_ERROR, data["CommandID"])
        self.__networkManager.sendPacket('', self.__listenningPort, p)       
        
    def __bootUpVM(self, data):
        """
        Procesa un paquete de arranque de máquina virtual
        Argumentos:
            data: diccionario con los datos del paquete
        Devuelve:
            Nada
        """
        vmID = data["VMID"]
        userID = data["UserID"]
        
        # Escoger el servidor de máquinas virtuales que alojará la máquina
        (serverID, errorDescription) = self.__loadBalancer.assignVMServer(vmID, MODE_T.BOOT_DOMAIN)
        if (errorDescription != None) :
            # Error => avisar al usuario
            p = self.__packetHandler.createErrorPacket(PACKET_T.VM_BOOT_FAILURE, errorDescription, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)
        else :           
            # Registrar los recursos de la máquina virtual
            familyID = self.__dbConnector.getFamilyID(vmID)
            familyFeatures = self.__dbConnector.getVanillaImageFamilyFeatures(familyID)
            self.__dbConnector.allocateVMServerResources(data["CommandID"], serverID, 
                                                         familyFeatures["RAMSize"], 0, familyFeatures["dataDiskSize"], 
                                                         familyFeatures["vCPUs"], 1)
            # Enviar la petición de arranque al servidor de máquinas virtuales
            p = self.__vmServerPacketHandler.createVMBootPacket(vmID, userID, data["CommandID"])
            serverData = self.__dbConnector.getVMServerBasicData(serverID)
            error = self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)    
            if (error != None) :
                p = self.__packetHandler.createErrorPacket(PACKET_T.VM_BOOT_FAILURE, 
                                                              ERROR_DESC_T.CLSRVR_VMSRVR_CONNECTION_LOST, data["CommandID"])
                self.__networkManager.sendPacket('', self.__listenningPort, p)
                self.__dbConnector.freeVMServerResources(data["CommandID"], True)
                return              
            # Guardar la ubicación de la nueva máquina virtual. 
            # Importante: todas las máquinas virtuales se identifican de forma única con el ID
            # del comando que las crea
            self.__dbConnector.registerActiveVMLocation(data["CommandID"], serverID)
            # Registrar el comando de arranque para controlar el tiempo de respuesta
            self.__dbConnector.registerVMBootCommand(data["CommandID"], data["VMID"])            
            
    def __auto_deploy_image(self, data):       
        
        if (data["Instances"] == 0 or data["Instances"] < -1) :
            p = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)        
            return  
        
        familyID = self.__dbConnector.getFamilyID(data["ImageID"])
        if (familyID == None) :
            p = self.__packetHandler.createErrorPacket(PACKET_T.AUTO_DEPLOY_ERROR, ERROR_DESC_T.CLSRVR_UNKNOWN_IMAGE, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)        
            return  
        
        familyFeatures = self.__dbConnector.getVanillaImageFamilyFeatures(familyID)
         
        if (data["Instances"] == -1) :
            if (not self.__dbConnector.isBeingDeleted(data["ImageID"])) :                 
                self.__dbConnector.changeImageStatus(data["ImageID"], IMAGE_STATE_T.DEPLOY)
                
                serverIDs = self.__dbConnector.getHosts(data["ImageID"], IMAGE_STATE_T.DEPLOY)
                if (serverIDs != []) :
                    self.__dbConnector.addImageEditionCommand(data["CommandID"], data["ImageID"]) 
                                       
                    # Enviar una petición de despliegue a todos los servidores arrancados que la tienen.
                    # A los demás, se la enviaremos cuando arranquen
                    p = self.__vmServerPacketHandler.createImageDeploymentPacket(self.__repositoryIP, self.__repositoryPort, data["ImageID"], data["CommandID"])
                    for serverID in serverIDs :
                        # Registrar los recursos en la BD
                        self.__dbConnector.allocateVMServerResources(data["CommandID"], serverID, 
                                                         0, familyFeatures["osDiskSize"] + familyFeatures["dataDiskSize"], 
                                                         0, 0, 1)
                        connectionData = self.__dbConnector.getVMServerBasicData(serverID)
                        self.__networkManager.sendPacket(connectionData["ServerIP"], connectionData["ServerPort"], p)   
                else :
                    # No hay nada que hacer => hemos terminado si ningún servidor apagado tiene la imagen
                    if (not self.__dbConnector.isThereSomeImageCopyInState(data["ImageID"], IMAGE_STATE_T.EDITED)) :
                        p = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])
                        self.__networkManager.sendPacket('', self.__listenningPort, p)
            else :
                # Error => avisar de él
                p = self.__packetHandler.createErrorPacket(PACKET_T.AUTO_DEPLOY_ERROR, ERROR_DESC_T.CLSRVR_NOT_EDITED_IMAGE, 
                                                                     data["CommandID"])
                self.__networkManager.sendPacket('', self.__listenningPort, p)  
        elif (data["Instances"] > 0) :
            if (self.__dbConnector.isAffectedByAutoDeploymentCommand(data["ImageID"])) :
                p = self.__packetHandler.createErrorPacket(PACKET_T.AUTO_DEPLOY_ERROR, ERROR_DESC_T.CLSRVR_AUTODEPLOYED, 
                                                                     data["CommandID"])
                self.__networkManager.sendPacket('', self.__listenningPort, p)  
                return
            # Ejecutamos el algoritmo de despliegue
            output = self.__loadBalancer.assignVMServer(data["ImageID"], MODE_T.DEPLOY_IMAGE)
            if (output[1] != None) :
                # Error => informamos de él y terminamos
                p = self.__packetHandler.createErrorPacket(PACKET_T.AUTO_DEPLOY_ERROR, output[1], data["CommandID"])
                self.__networkManager.sendPacket('', self.__listenningPort, p)  
            else :
                if (output[2] < data["Instances"]) :
                    # No podemos cumplir con lo que nos piden => error
                    p = self.__packetHandler.createErrorPacket(PACKET_T.AUTO_DEPLOY_ERROR, 
                                                                  ERROR_DESC_T.CLSRVR_AUTOD_TOO_MANY_INSTANCES, data["CommandID"])
                    self.__networkManager.sendPacket('', self.__listenningPort, p)  
                else :
                    
                    # Todo ha ido bien => preparamos los paquetes de despliegue                    
                    servers = []
                    deployed_copies = 0
                    i = 0
                    while (deployed_copies < data["Instances"]) :
                        servers.append(output[i][0][0])                             
                        deployed_copies += output[i][0][1]
                        i += 1
                                                
                    # Registramos la petición de despliegue automático
                    self.__dbConnector.addAutoDeploymentCommand(data["CommandID"], data["ImageID"], len(servers))
                    
                    # Enviamos los paquetes de despliegue                    
                    p = self.__vmServerPacketHandler.createImageDeploymentPacket(self.__repositoryIP, self.__repositoryPort, data["ImageID"], data["CommandID"])                    
                    for serverID in servers:                        
                        # Registrar los recursos en la BD
                        self.__dbConnector.allocateVMServerResources(data["CommandID"], serverID, 
                                                         0, familyFeatures["osDiskSize"] + familyFeatures["dataDiskSize"], 
                                                         0, 0, 1)
                        # Enviar los paquetes
                        connectionData = self.__dbConnector.getVMServerBasicData(serverID)            
                        self.__networkManager.sendPacket(connectionData["ServerIP"], connectionData["ServerPort"], p)     

    def __deleteImageFromInfrastructure(self, data):
        errorDescription = None
        if (self.__dbConnector.isBeingEdited(data["ImageID"])) :
            errorDescription = ERROR_DESC_T.CLSRVR_LOCKED_IMAGE
        elif (self.__dbConnector.isBeingDeleted(data["ImageID"])) :
            errorDescription = ERROR_DESC_T.CLSRVR_DELETED_IMAGE
        elif (self.__dbConnector.getFamilyID(data["ImageID"]) == None) :
            errorDescription = ERROR_DESC_T.CLSRVR_UNKNOWN_IMAGE
        if (errorDescription != None) :
            p = self.__packetHandler.createErrorPacket(PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR, errorDescription, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)
        else :
            # Impedimos que se arranquen más copias de la imagen
            self.__dbConnector.changeImageStatus(data["ImageID"], IMAGE_STATE_T.DELETE)
            # Borramos la asociación entre una imagen y una familia de imágenes
            self.__dbConnector.deleteFamilyID(data["ImageID"])
            # Registramos el comando en la base de datos
            self.__dbConnector.addImageDeletionCommand(data["CommandID"], data["ImageID"])
            # Borramos la imagen del repositorio
            p = self.__imageRepositoryPacketHandler.createDeleteRequestPacket(data["ImageID"])
            self.__networkManager.sendPacket(self.__repositoryIP, self.__repositoryPort, p)        
            # Borrar la máquina de todos los servidores arrancados que la tengan
            p = self.__vmServerPacketHandler.createDeleteImagePacket(data["ImageID"], data["CommandID"])
            
            for serverID in self.__dbConnector.getHosts(data["ImageID"], IMAGE_STATE_T.DELETE) :
                serverData = self.__dbConnector.getVMServerBasicData(serverID)
                self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)
               
            
    def __createOrEditImage(self, data):                      
        errorDescription = None
        
        # Averiguar si la imagen ya se está editando, borrando o no existe        
        if (self.__dbConnector.isBeingEdited(data["ImageID"])) :
            errorDescription = ERROR_DESC_T.CLSRVR_LOCKED_IMAGE
        elif (self.__dbConnector.isBeingDeleted(data["ImageID"])) :    
            errorDescription = ERROR_DESC_T.CLSRVR_DELETED_IMAGE
        elif (self.__dbConnector.getFamilyID(data["ImageID"]) == None) :
            errorDescription = ERROR_DESC_T.CLSRVR_UNKNOWN_IMAGE
        elif (data["packet_type"] == PACKET_T.CREATE_IMAGE):
            repositoryStatus = self.__dbConnector.getImageRepositoryStatus(self.__repositoryIP, self.__repositoryPort)
            if (repositoryStatus == None) :
                errorDescription = ERROR_DESC_T.CLSRVR_IR_CONNECTION_ERROR
            else :
                imageFeatures = self.__dbConnector.getVanillaImageFamilyFeatures(self.__dbConnector.getFamilyID(data["ImageID"]))
                required_disk_space = imageFeatures["osDiskSize"] + imageFeatures["dataDiskSize"]
                required_disk_space = self.__averageCompressionRatio * required_disk_space
                remaining_disk_space = repositoryStatus["FreeDiskSpace"] - required_disk_space
                if (remaining_disk_space < 0) :
                    errorDescription = ERROR_DESC_T.CLSRVR_IR_NO_DISK_SPACE
        
        if (errorDescription != None) :        
            if (data["packet_type"] == PACKET_T.CREATE_IMAGE) :
                packet_type = PACKET_T.IMAGE_CREATION_ERROR
            else :
                packet_type = PACKET_T.IMAGE_EDITION_ERROR  
            p = self.__packetHandler.createErrorPacket(packet_type, errorDescription, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)
            return           
        
        # Encontrar un servidor vanilla
        (serverID, errorDescription) = self.__loadBalancer.assignVMServer(data["ImageID"], MODE_T.CREATE_OR_EDIT_IMAGE)
        if (errorDescription != None) :
            # Error => informar de él y terminar
            if (data["packet_type"] == PACKET_T.CREATE_IMAGE) :
                packet_type = PACKET_T.IMAGE_CREATION_ERROR
            else :
                packet_type = PACKET_T.IMAGE_EDITION_ERROR
            p = self.__packetHandler.createErrorPacket(packet_type, errorDescription, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)
            return
        
        # Ya tenemos un servidor vanilla 
        if (data["packet_type"] == PACKET_T.CREATE_IMAGE) :
            # Registramos la nueva imagen en la BD
            self.__dbConnector.registerNewVMVanillaImageFamily(data["CommandID"], self.__dbConnector.getFamilyID(data["ImageID"]))
            modify = False
        else :
            # Registramos el comando de edición en la BD
            self.__dbConnector.addImageEditionCommand(data["CommandID"], data["ImageID"])
            modify = True
            
        # Registrar los recursos consumidos por la máquina virtual
        familyID = self.__dbConnector.getFamilyID(data["ImageID"])
        familyFeatures = self.__dbConnector.getVanillaImageFamilyFeatures(familyID)
        self.__dbConnector.allocateVMServerResources(data["CommandID"], serverID, 
                                                         familyFeatures["RAMSize"], familyFeatures["osDiskSize"] + familyFeatures["dataDiskSize"], 0, 
                                                         familyFeatures["vCPUs"], 1)
        self.__dbConnector.allocateImageRepositoryResources(self.__repositoryIP, self.__repositoryPort, data["CommandID"], 
                                                            familyFeatures["osDiskSize"] + familyFeatures["dataDiskSize"])
        
        connectionData = self.__dbConnector.getVMServerBasicData(serverID)
        p = self.__vmServerPacketHandler.createImageEditionPacket(self.__repositoryIP, self.__repositoryPort, data["ImageID"], modify, data["CommandID"], 
                                                                  data["OwnerID"])
        self.__networkManager.sendPacket(connectionData["ServerIP"], connectionData["ServerPort"], p)
        self.__dbConnector.registerActiveVMLocation(data["CommandID"], serverID)        
            
    def __deployOrDeleteImage(self, data):
        serverNameOrIPAddress = data["ServerNameOrIPAddress"]
        serverID = self.__dbConnector.getVMServerID(serverNameOrIPAddress)        
        serverData = self.__dbConnector.getVMServerBasicData(serverID)
        errorDescription = None        
            
        # Comprobar que la imagen existe
        if (self.__dbConnector.isBeingEdited(data["ImageID"])) :
            errorDescription = ERROR_DESC_T.CLSRVR_LOCKED_IMAGE
        elif (self.__dbConnector.isBeingDeleted(data["ImageID"])):
            errorDescription = ERROR_DESC_T.CLSRVR_DELETED_IMAGE
        elif (self.__dbConnector.getFamilyID(data["ImageID"]) == None) :
            errorDescription = ERROR_DESC_T.CLSRVR_UNKNOWN_IMAGE
        elif (serverID == None) :
            errorDescription =  ERROR_DESC_T.CLSRVR_UNKNOWN_VMSRVR
        elif (serverData["ServerStatus"] != SERVER_STATE_T.READY):
            errorDescription = ERROR_DESC_T.CLSRVR_VMSRVR_NOT_READY
        elif (data["packet_type"] == PACKET_T.DEPLOY_IMAGE and self.__dbConnector.hostsImage(serverID, data["ImageID"]))\
            or (data["packet_type"] == PACKET_T.DELETE_IMAGE_FROM_SERVER and not self.__dbConnector.hostsImage(serverID, data["ImageID"])):
            
            if (data["packet_type"] == PACKET_T.DEPLOY_IMAGE):
                errorDescription = ERROR_DESC_T.CLSRVR_IMAGE_HOSTED_ON_VMSRVR
            else :
                errorDescription = ERROR_DESC_T.CLSRVR_IMAGE_NOT_HOSTED_ON_VMSRVR
        elif (data["packet_type"] == PACKET_T.DEPLOY_IMAGE):
            # Comprobar que la imagen cabe
            free_disk_space = self.__dbConnector.getVMServerStatistics(serverID)["FreeStorageSpace"]
            familyID = self.__dbConnector.getFamilyID(data["ImageID"])
            familyFeatures = self.__dbConnector.getVanillaImageFamilyFeatures(familyID)
            required_disk_space = familyFeatures["osDiskSize"] + familyFeatures["dataDiskSize"]
            if (free_disk_space < required_disk_space) :
                errorDescription = ERROR_DESC_T.CLSRVR_VMSRVR_NO_DISK_SPACE
            
        if (errorDescription != None) :       
            if (data["packet_type"] == PACKET_T.DEPLOY_IMAGE):
                error_type = PACKET_T.IMAGE_DEPLOYMENT_ERROR
            else:
                error_type = PACKET_T.DELETE_IMAGE_FROM_SERVER_ERROR 
            p = self.__packetHandler.createErrorPacket(error_type, errorDescription, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, p)
            return
           
        # Todo es correcto => registrar los recursos consumidos, enviar la petición
        if (data["packet_type"] == PACKET_T.DEPLOY_IMAGE) :
            # Registrar los recursos que consumirá la imagen
            familyID = self.__dbConnector.getFamilyID(data["ImageID"])
            familyFeatures = self.__dbConnector.getVanillaImageFamilyFeatures(familyID)
            self.__dbConnector.allocateVMServerResources(data["CommandID"], serverID, 0, familyFeatures["osDiskSize"] + familyFeatures["dataDiskSize"], 
                                                         0, 0, 0)
            p = self.__vmServerPacketHandler.createImageDeploymentPacket(self.__repositoryIP, self.__repositoryPort, data["ImageID"], data["CommandID"])
        else:
            p = self.__vmServerPacketHandler.createDeleteImagePacket(data["ImageID"], data["CommandID"])
        self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)
        
        
            
    def __sendRepositoryStatusData(self):
        repositoryStatus = self.__dbConnector.getImageRepositoryStatus(self.__repositoryIP, self.__repositoryPort)
        p = self.__packetHandler.createRepositoryStatusPacket(repositoryStatus["FreeDiskSpace"], 
                                                                 repositoryStatus["AvailableDiskSpace"], 
                                                                 repositoryStatus["ConnectionStatus"])
        self.__networkManager.sendPacket('', self.__listenningPort, p)
        
    def __unregisterOrShutdownVMServer(self, data):
        """
        Procesa un paquete de apagado o borrado de un servidor de máquinas virtuales
        Argumentos:
            data: diccionario con los datos del paquete
        Devuelve:
            nada
        """
        key = data["ServerNameOrIPAddress"] 
        haltServer = data["Halt"]
        unregister = data["Unregister"]
        
        if data.has_key("CommandID") :
            useCommandID = True 
            commandID = data["CommandID"]
        else :
            useCommandID = False
            commandID = ""
            
        # Paso 1: averiguar si existe el servidor
        serverID = self.__dbConnector.getVMServerID(key)
        if (serverID == None) :            
            if (unregister) :
                packet_type = PACKET_T.VM_SERVER_UNREGISTRATION_ERROR
            else :
                packet_type = PACKET_T.VM_SERVER_SHUTDOWN_ERROR
            p = self.__packetHandler.createErrorPacket(packet_type, key, ERROR_DESC_T.CLSRVR_UNKNOWN_VMSRVR, commandID)
            self.__networkManager.sendPacket('', self.__listenningPort, p)  
            return
        
        # Paso 2: sabemos que el servidor existe. Si está arrancado, lo paramos 
        serverData = self.__dbConnector.getVMServerBasicData(serverID)            
        status = serverData["ServerStatus"]    
        if (status == SERVER_STATE_T.READY or status == SERVER_STATE_T.BOOTING) :  
            try :
                connectionReady = self.__networkManager.isConnectionReady(serverData["ServerIP"], serverData["ServerPort"])
            except Exception:
                connectionReady = False                 
            if (not connectionReady) :   
                if (unregister) :
                    packet_type = PACKET_T.VM_SERVER_UNREGISTRATION_ERROR
                else :
                    packet_type = PACKET_T.VM_SERVER_SHUTDOWN_ERROR
                p = self.__packetHandler.createErrorPacket(packet_type, ERROR_DESC_T.CLSRVR_VMSRVR_CONNECTION_ERROR, commandID)
                self.__networkManager.sendPacket('', self.__listenningPort, p)  
                return
            
            # La conexión está lista => enviamos el paquete de apagado
            self.__dbConnector.deleteHostedVMs(serverID)
            if not haltServer :
                p = self.__vmServerPacketHandler.createVMServerShutdownPacket()
            else :
                p = self.__vmServerPacketHandler.createVMServerHaltPacket()
                self.__networkManager.sendPacket(serverData["ServerIP"], serverData["ServerPort"], p)
                     
            # Cerramos la conexión 
            self.__networkManager.closeConnection(serverData["ServerIP"], serverData["ServerPort"])       
            
        # Paso 3: borramos el servidor de la base de datos (sólo si es necesario)      
        if (unregister) :
            self.__dbConnector.deleteVMServer(key)
            
        # Paso 4: respondemos a la web (sólo si es necesario)      
        if (useCommandID) :
            p = self.__packetHandler.createCommandExecutedPacket(commandID)
        
    def __sendStatusData(self, queryMethod, packetCreationMethod):
        """
        Envía información de estado al endpoint de la web
        Argumentos:
            queryMethod: el método que extraerá la información de estado de la base de datos
            packetCreationMethod: el método que creará los paquetes de estado
        Devuelve:
            Nada
        """        
        # La información de las tablas se fragmenta en varios segmentos para no superar
        # el tamaño máximo del paquete (64 KB)
        
        segmentSize = 100 # Cada segmento llevará 100 filas de la tabla
        outgoingData = []
        serverIDs = self.__dbConnector.getVMServerIDs()
        if (len(serverIDs) == 0) :
            # No hay datos => responder con segmento vacío
            segmentCounter = 0
            segmentNumber = 0
            sendLastSegment = True
        else :
            # Hay datos => calcular el número de segmentos que necesitamos
            segmentCounter = 1        
            segmentNumber = (len(serverIDs) / segmentSize)
            if (len(serverIDs) % segmentSize != 0) :
                segmentNumber += 1
                sendLastSegment = True
            else :
                # Si la división no es exacta, hay que enviar un último segmento con lo que quede
                sendLastSegment = False  
                
        # Crear los segmentos y enviarlos cuando estén llenos
        for serverID in serverIDs :
            row = queryMethod(serverID)
            if (row == None):
                break
            if (isinstance(row, dict)) :
                outgoingData.append(row)
            else :
                outgoingData += row
                
            if (len(outgoingData) >= segmentSize) :
                packet = packetCreationMethod(segmentCounter, segmentNumber, outgoingData)
                self.__networkManager.sendPacket('', self.__listenningPort, packet)
                outgoingData = []
                segmentCounter += 1
                
        # Enviar un segmento con los datos que quedan (sólo si hace falta)
        if (sendLastSegment) :
            packet = packetCreationMethod(segmentCounter, segmentNumber, outgoingData)
            self.__networkManager.sendPacket('', self.__listenningPort, packet) 
            
    def __doImmediateShutdown(self, data):
        """
        Apaga TODAS las máquinas del cluster, incluyendo los servidores de máquinas virtuales.
        Argumentos:
            data: diccionario con los datos del paquete
        Devuelve:
            Nada
        """    
        # Apagamos el repositorio
        p = self.__imageRepositoryPacketHandler.createHaltPacket()
        self.__networkManager.sendPacket(self.__repositoryIP, self.__repositoryPort, p)
        self.__networkManager.closeConnection(self.__repositoryIP, self.__repositoryPort)
        vmServersConnectionData = self.__dbConnector.getActiveVMServersConnectionData()
        if (vmServersConnectionData != None) :
            args = dict()
            args["Halt"] = data["HaltVMServers"]
            args["Unregister"] = False            
            for connectionData in vmServersConnectionData :
                args["ServerNameOrIPAddress"] = connectionData["ServerIP"]
                self.__unregisterOrShutdownVMServer(args)  
        self.__finished = True       
        
    def __requestVNCConnectionData(self):
        """
        Solicita los datos de conexión VNC a todos los servidores de máquinas virtuales.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        p = self.__vmServerPacketHandler.createVMServerDataRequestPacket(VMSRVR_PACKET_T.QUERY_ACTIVE_VM_DATA)
        
        connectionData = self.__dbConnector.getActiveVMServersConnectionData()
        for cd in connectionData :            
            errorMessage = self.__networkManager.sendPacket(cd["ServerIP"], cd["ServerPort"], p)
            NetworkManager.printConnectionWarningIfNecessary(cd["ServerIP"], cd["ServerPort"], "VNC connection data request", errorMessage)   
            
    def __destroyDomain(self, data):
        """
        Destruye una máquina virtual activa
        Argumentos:
            data: diccionario con los datos del paquete correspondiente
        Devuelve:
            Nada
        """
        # Comprobar si la máquina existe
        serverID = self.__dbConnector.getActiveVMHostID(data["DomainID"])
        if (serverID == None) :
            # Error
            packet = self.__packetHandler.createErrorPacket(PACKET_T.DOMAIN_DESTRUCTION_ERROR, 
                                                                      ERROR_DESC_T.CLSRVR_DOMAIN_NOT_REGISTERED, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, packet)
            return       
        
        # Averiguar los datos del servidor y pedirle que se la cargue
        connectionData = self.__dbConnector.getVMServerBasicData(serverID)
        packet = self.__vmServerPacketHandler.createVMShutdownPacket(data["DomainID"])
        errorMessage = self.__networkManager.sendPacket(connectionData["ServerIP"], connectionData["ServerPort"], packet)
        if (errorMessage != None) :
            packet = self.__packetHandler.createErrorPacket(PACKET_T.DOMAIN_DESTRUCTION_ERROR, 
                                                                                ERROR_DESC_T.CLSRVR_VMSRVR_CONNECTION_LOST, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, packet)
        else :
            # Borrar la máquina virtual de la base de datos           
            self.__dbConnector.deleteActiveVMLocation(data["CommandID"])         
            # Indicar al endpoint que todo fue bien
            packet = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, packet)
            
    def __changeVMServerConfiguration(self, data):
        serverID = self.__dbConnector.getVMServerID(data["ServerNameOrIPAddress"])
        
        if (serverID == None) :
            packet = self.__packetHandler.createErrorPacket(PACKET_T.VM_SERVER_CONFIGURATION_CHANGE_ERROR,
                ERROR_DESC_T.CLSRVR_UNKNOWN_VMSRVR, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, packet)
            return
        
        status = self.__dbConnector.getVMServerBasicData(serverID)["ServerStatus"]
        
        if (status == SERVER_STATE_T.BOOTING or status == SERVER_STATE_T.READY) :
            packet = self.__packetHandler.createErrorPacket(PACKET_T.VM_SERVER_CONFIGURATION_CHANGE_ERROR,
                ERROR_DESC_T.CLSRVR_ACTIVE_VMSRVR, data["CommandID"])
            self.__networkManager.sendPacket('', self.__listenningPort, packet)
            return
            
        try :
            self.__dbConnector.setServerBasicData(serverID, data["NewVMServerName"], SERVER_STATE_T.SHUT_DOWN, 
                                                  data["NewVMServerIPAddress"], data["NewVMServerPort"], data["NewVanillaImageEditionBehavior"])
            packet = self.__packetHandler.createCommandExecutedPacket(data["CommandID"])
        
        except Exception :
            packet = self.__packetHandler.createErrorPacket(PACKET_T.VM_SERVER_CONFIGURATION_CHANGE_ERROR,
               ERROR_DESC_T.CLSRVR_VMSRVR_IDS_IN_USE, data["CommandID"])
            
        self.__networkManager.sendPacket('', self.__listenningPort, packet)    
        
    def hasFinished(self):
        return self.__finished