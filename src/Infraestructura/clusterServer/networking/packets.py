# -*- coding: utf8 -*-
'''
Gestor de paquetes del servidor de cluster
@author: Luis Barrios Hernández
@version: 4.0
'''

from ccutils.enums import enum

CLUSTER_SERVER_PACKET_T = enum("REGISTER_VM_SERVER", "VM_SERVER_REGISTRATION_ERROR", "QUERY_VM_SERVERS_STATUS",
                            "VM_SERVERS_STATUS_DATA", "QUERY_VM_DISTRIBUTION", "VM_DISTRIBUTION_DATA",
                            "UNREGISTER_OR_SHUTDOWN_VM_SERVER", "BOOTUP_VM_SERVER",
                            "VM_SERVER_BOOTUP_ERROR", "VM_BOOT_REQUEST", "VM_CONNECTION_DATA", "VM_BOOT_FAILURE", 
                            "HALT", "QUERY_ACTIVE_VM_DATA", "ACTIVE_VM_DATA", "COMMAND_EXECUTED", "VM_SERVER_SHUTDOWN_ERROR",
                            "VM_SERVER_UNREGISTRATION_ERROR", "DOMAIN_DESTRUCTION", "DOMAIN_DESTRUCTION_ERROR", 
                            "VM_SERVER_CONFIGURATION_CHANGE", "VM_SERVER_CONFIGURATION_CHANGE_ERROR",
                            "GET_IMAGE", "SET_IMAGE", "QUERY_REPOSITORY_STATUS", "REPOSITORY_STATUS",
                            "DEPLOY_IMAGE", "IMAGE_DEPLOYMENT_ERROR", "IMAGE_DEPLOYED", "DELETE_IMAGE_FROM_SERVER", "DELETE_IMAGE_FROM_SERVER_ERROR",
                            "IMAGE_DELETED", "CREATE_IMAGE", "IMAGE_CREATION_ERROR", "IMAGE_CREATED", "EDIT_IMAGE", "IMAGE_EDITION_ERROR",
                            "DELETE_IMAGE_FROM_INFRASTRUCTURE", "DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR", "AUTO_DEPLOY", "AUTO_DEPLOY_ERROR",
                            "VM_SERVER_INTERNAL_ERROR", "QUERY_VM_SERVERS_RESOURCE_USAGE", "VM_SERVERS_RESOURCE_USAGE")

class ClusterServerPacketHandler(object):
    """
    Estos objetos leen y escriben los paquetes que el endpoint y el servidor de cluster utilizan para
    comunicarse.
    """    
    def __init__(self, packetCreator):
        """
        Inicializa el estado del gestor de paquetes
        Argumentos:
            packetCreator: el objeto NetworkManager que utilizaremos para crear los paquetes
        """
        self.__packetCreator = packetCreator
        
    def createErrorPacket(self, packet_type, errorDescription, commandID):
        p = self.__packetCreator.createPacket(3)
        p.writeInt(packet_type)
        p.writeInt(errorDescription)
        p.writeString(commandID)
        return p
        
    def createAutoDeployPacket(self, imageID, instances, commandID):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(CLUSTER_SERVER_PACKET_T.AUTO_DEPLOY)
        p.writeInt(imageID)
        p.writeInt(instances)
        p.writeString(commandID)
        return p
            
    def createVMServerRegistrationPacket(self, IPAddress, port, name, isVanillaServer, commandID):
        """
        Crea un paquete de registro de una máquina virtual
        Argumentos:
            IPAddress: la dirección IP del servidor
            port: su puerto
            name: el nombre del servidor de máquinas virtuales
            isVanillaServer: indica si el servidor de máquinas virtuales se utilizará preferentemente
            para editar imágenes o no.
            commandID: el identificador único del comando de arranque
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(CLUSTER_SERVER_PACKET_T.REGISTER_VM_SERVER)
        p.writeString(IPAddress)
        p.writeInt(port)
        p.writeString(name)
        p.writeBool(isVanillaServer)
        p.writeString(commandID)
        return p
    
    def createCommandExecutedPacket(self, commandID):
        """
        Crea un paquete que indica que un comando se ha ejecutado.
        Argumentos:
            commandID: el identificador único del comando
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(CLUSTER_SERVER_PACKET_T.COMMAND_EXECUTED)
        p.writeString(commandID)
        return p  
    
    def createImageEditedPacket(self, commandID, imageID):  
        p = self.__packetCreator.createPacket(3)
        p.writeInt(CLUSTER_SERVER_PACKET_T.COMMAND_EXECUTED)
        p.writeString(commandID)
        p.writeInt(imageID)
        return p  
    
    def createDataRequestPacket(self, query):
        """
        Crea un paquete de solicitud de estado
        Argumentos:
            query: la información de estado que queremos recuperar
            (p.e. máquinas virtuales activas, imágenes que se pueden arrancar,...)
         Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(query)
        return p
    
    def createVMServerStatusPacket(self, segment, sequenceSize, data):
        """
        Crea un paquete con el estado de un servidor de máquinas virtuales
        Argumentos:
            segment: posición del segmento en la secuencia
            sequenceSize: tamaño de la secuencia (en segmentos)
            data: los datos del segmento
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(CLUSTER_SERVER_PACKET_T.VM_SERVERS_STATUS_DATA)
        p.writeInt(segment)
        p.writeInt(sequenceSize)
        for row in data :
            p.writeString(row["ServerName"])
            p.writeInt(row["ServerStatus"])
            p.writeString(row["ServerIP"])
            p.writeInt(int(row["ServerPort"]))   
            p.writeBool(int(row["IsVanillaServer"]) == 1)         
        return p
    
    def createVMDistributionPacket(self, segment, sequenceSize, data):
        """
        Crea un paquete que contiene la distribución de las máquinas virtuales
        Argumentos:
            segment: posición del segmento en la secuencia
            sequenceSize: tamaño de la secuencia (en segmentos)
            data: los datos del segmento
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(CLUSTER_SERVER_PACKET_T.VM_DISTRIBUTION_DATA)
        p.writeInt(segment)
        p.writeInt(sequenceSize)
        for row in data :
            p.writeString(row["ServerName"])
            p.writeInt(row["ImageID"])
            p.writeInt(row["CopyStatus"])
        return p
    
    def createVMServerUnregistrationOrShutdownPacket(self, serverNameOrIPAddress, isShutDown, unregister, commandID):
        """
        Crea un paquete de apagado o borrado de un servidor de máquinas virtuales
        Argumentos:
            serverNameOrIPAddress: el nombre del servidor o su dirección IP
            isShutDown: Si es True, los dominios se destuirán inmediatamente. Si es False, se esparará a que
            los usuarios los apaguen. 
            unregister: Si es True el servidor se borrará; si es False sólo se apagará
            commandID: el identificador único del comando
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(CLUSTER_SERVER_PACKET_T.UNREGISTER_OR_SHUTDOWN_VM_SERVER)
        p.writeString(serverNameOrIPAddress)
        p.writeBool(isShutDown)
        p.writeBool(unregister)
        p.writeString(commandID)
        return p
    
    def createVMServerBootUpPacket(self, serverNameOrIPAddress, commandID):
        """
        Crea un paquete de arranque de un servidor de máquinas virtuales
        Argumentos:
            serverNameOrIPAddress: el nombre o la IP del servidor
            commandID: el identificador único del comando
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(CLUSTER_SERVER_PACKET_T.BOOTUP_VM_SERVER)
        p.writeString(serverNameOrIPAddress)
        p.writeString(commandID)
        return p
    
    def createVMBootRequestPacket(self, imageID, userID, commandID):
        """
        Crea un paquete de arranque de máuqina virtual
        Argumentos:
            imageID: identificador de la imagen a arrancar
            userID: identificador del propietario de la máquina
            commandID: el identificador único del comando
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(4)
        p.writeInt(CLUSTER_SERVER_PACKET_T.VM_BOOT_REQUEST)
        p.writeInt(imageID)
        p.writeInt(userID)
        p.writeString(commandID)
        return p
    
    def createVMConnectionDataPacket(self, IPAddress, port, password, commandID):
        """
        Crea un paquete con los datos de conexión a una máquina virtual
        Argumentos:
            IPAddress: dirección IP del servidor VNC
            port: puerto del servidor VNC
            password: contraseña del servidor VNC
            commandID: identificador único del comando
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(4)
        p.writeInt(CLUSTER_SERVER_PACKET_T.VM_CONNECTION_DATA)
        p.writeString(IPAddress)
        p.writeInt(port)
        p.writeString(password)
        p.writeString(commandID)
        return p
    
    def createActiveVMsDataPacket(self, data):
        """
        Crea un paquete que contiene los datos de conexión de varias máquinas virtuales
        del mismo servidor
        Argumentos:
            data: un string con los datos a enviar
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(CLUSTER_SERVER_PACKET_T.ACTIVE_VM_DATA)
        p.dumpData(data)
        return p
    
    def createHaltPacket(self, haltServers):
        """
        Crea un paquete que apagará el servidor de cluster.
        Argumentos:
            haltServers: si es True, los servidores de máquinas virtuales se cargarán todos los
            dominios inmediatamente. Si es False, esperarán a que los usuarios los apaguen.
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(1)
        p.writeInt(CLUSTER_SERVER_PACKET_T.HALT)
        p.writeBool(haltServers)
        return p
    
    def createDomainDestructionPacket(self, domainID, commandID):
        """
        Crea un paquete de destrucción de dominios
        Argumentos:
            domainID: el identificador único del dominio a destruir
            commandID: el identificador único del comando
        Devuelve:
            un paquete con los datos de los argumentos
        """
        p = self.__packetCreator.createPacket(4) # Todo lo que sea liberar carga es bueno. Por eso es ligeramente más prioritario que los otros
        p.writeInt(CLUSTER_SERVER_PACKET_T.DOMAIN_DESTRUCTION)
        p.writeString(domainID)
        p.writeString(commandID)
        return p
    
    def createRepositoryStatusPacket(self, freeDiskSpace, availableDiskSpace, status):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(CLUSTER_SERVER_PACKET_T.REPOSITORY_STATUS)
        p.writeInt(freeDiskSpace)
        p.writeInt(availableDiskSpace)
        p.writeInt(status)
        return p
        
    def createVMServerConfigurationChangePacket(self, serverNameOrIPAddress, newName, newIPAddress, newPort, newVanillaImageEditionBehavior, commandID):
        p = self.__packetCreator.createPacket(2)
        p.writeInt(CLUSTER_SERVER_PACKET_T.VM_SERVER_CONFIGURATION_CHANGE)
        p.writeString(serverNameOrIPAddress)
        p.writeString(newName)
        p.writeString(newIPAddress)
        p.writeInt(newPort)
        p.writeBool(newVanillaImageEditionBehavior)
        p.writeString(commandID)
        return p
        
    def createImageDeploymentPacket(self, packet_type, serverNameOrIPAddress, imageID, commandID):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(packet_type)    
        p.writeString(serverNameOrIPAddress)    
        p.writeInt(imageID)
        p.writeString(commandID)
        return p
    
    def createImageEditionPacket(self, packet_type, imageID, ownerID, commandID):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(packet_type)
        p.writeInt(imageID)
        p.writeInt(ownerID)
        p.writeString(commandID)
        return p
    
    def createImageDeletionPacket(self, imageID, commandID):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(CLUSTER_SERVER_PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE)
        p.writeInt(imageID)
        p.writeString(commandID)
        return p
    
    def createVMServerResourceUsagePacket(self, segment, sequenceSize, data):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(CLUSTER_SERVER_PACKET_T.VM_SERVERS_RESOURCE_USAGE)
        p.writeInt(segment)
        p.writeInt(sequenceSize)
        for row in data :
            p.writeString(row["ServerName"])
            p.writeInt(row["ActiveHosts"])
            p.writeInt(row["RAMInUse"])
            p.writeInt(row["RAMSize"])
            p.writeInt(row["FreeStorageSpace"])
            p.writeInt(row["AvailableStorageSpace"])
            p.writeInt(row["FreeTemporarySpace"])
            p.writeInt(row["AvailableTemporarySpace"])
            p.writeInt(row["ActiveVCPUs"])
            p.writeInt(row["PhysicalCPUs"])
        return p
    
    def readPacket(self, p):
        """
        Lee un paquete intercambiado por el endpoint y el servidor de cluster
        Argumentos:
            p: el paquete a leer
        Devuelve:
            Un diccionario con el contenido del paquete. El tipo del paquete se guardará bajo la clave
            packet_type.
        """
        result = dict()
        packet_type = p.readInt()
        result["packet_type"] = packet_type        
        if (packet_type == CLUSTER_SERVER_PACKET_T.REGISTER_VM_SERVER) :
            result["VMServerIP"] = p.readString()
            result["VMServerPort"] = p.readInt()
            result["VMServerName"] = p.readString()
            result["IsVanillaServer"] = p.readBool()
            result["CommandID"] = p.readString()        
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVERS_STATUS_DATA) :
            result["Segment"] = p.readInt()
            result["SequenceSize"] = p.readInt()
            data = []
            while (p.hasMoreData()) :
                data.append((p.readString(), p.readInt(), p.readString(), p.readInt(), p.readBool()))
            result["Data"] = data
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.VM_DISTRIBUTION_DATA) :
            result["Segment"] = p.readInt()
            result["SequenceSize"] = p.readInt()
            data = []
            while (p.hasMoreData()) :
                data.append((p.readString(), p.readInt(), p.readInt()))
            result["Data"] = data
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.ACTIVE_VM_DATA) :
            result["Segment"] = p.readInt()
            result["SequenceSize"] = p.readInt()
            result["VMServerIP"] = p.readString()
            data = []
            while (p.hasMoreData()) :
                data.append((p.readString(), p.readInt(), p.readInt(), p.readString(), p.readInt(), p.readString()))
            result["Data"] = data
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVERS_RESOURCE_USAGE):
            result["Segment"] = p.readInt()
            result["SequenceSize"] = p.readInt()
            data = []
            while (p.hasMoreData()) :
                data.append((p.readString(), p.readInt(), p.readInt(), p.readInt(), p.readInt(), p.readInt(), p.readInt(), p.readInt(), p.readInt(), p.readInt()))
            result["Data"] = data
                
        elif (packet_type == CLUSTER_SERVER_PACKET_T.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
            result["ServerNameOrIPAddress"] = p.readString()
            result["Halt"] =  p.readBool()
            result["Unregister"] = p.readBool()
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.BOOTUP_VM_SERVER) :
            result["ServerNameOrIPAddress"] = p.readString()
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.DEPLOY_IMAGE or
              packet_type == CLUSTER_SERVER_PACKET_T.DELETE_IMAGE_FROM_SERVER) :
            result["ServerNameOrIPAddress"] = p.readString()
            result["ImageID"] = p.readInt()
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.VM_BOOT_REQUEST):
            result["VMID"] = p.readInt()
            result["UserID"] = p.readInt()
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.VM_CONNECTION_DATA):
            result["VNCServerIPAddress"] = p.readString()
            result["VNCServerPort"] = p.readInt()
            result["VNCServerPassword"] = p.readString()
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.HALT) :
            result["HaltVMServers"] = p.readBool()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.COMMAND_EXECUTED) :
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.DOMAIN_DESTRUCTION) :
            result["DomainID"] = p.readString()
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVER_CONFIGURATION_CHANGE): 
            result["ServerNameOrIPAddress"] = p.readString()    
            result["NewVMServerName"] = p.readString()
            result["NewVMServerIPAddress"] = p.readString()
            result["NewVMServerPort"] = p.readInt()
            result["NewVanillaImageEditionBehavior"] = p.readBool()
            result["CommandID"] = p.readString() 
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.REPOSITORY_STATUS) :
            result["FreeDiskSpace"] = p.readInt()
            result["AvailableDiskSpace"] = p.readInt()
            result["RepositoryStatus"] = p.readInt()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.CREATE_IMAGE or 
              packet_type == CLUSTER_SERVER_PACKET_T.EDIT_IMAGE):
            result["ImageID"] = p.readInt()
            result["OwnerID"] = p.readInt()
            result["CommandID"] = p.readString() 
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE) :
            result["ImageID"] = p.readInt()
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.AUTO_DEPLOY):
            result["ImageID"] = p.readInt()
            result["Instances"] = p.readInt()
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVER_INTERNAL_ERROR):
            result["CommandID"] = p.readString()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.IMAGE_CREATED):
            result["CommandID"] = p.readString()
            result["ImageID"] = p.readInt()
            
        elif (packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVER_REGISTRATION_ERROR or 
              packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVER_BOOTUP_ERROR or 
              packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVER_UNREGISTRATION_ERROR or 
              packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVER_SHUTDOWN_ERROR or
              packet_type == CLUSTER_SERVER_PACKET_T.IMAGE_DEPLOYMENT_ERROR or
              packet_type == CLUSTER_SERVER_PACKET_T.DELETE_IMAGE_FROM_SERVER_ERROR or 
              packet_type == CLUSTER_SERVER_PACKET_T.VM_BOOT_FAILURE or 
              packet_type == CLUSTER_SERVER_PACKET_T.DOMAIN_DESTRUCTION_ERROR or
              packet_type == CLUSTER_SERVER_PACKET_T.VM_SERVER_CONFIGURATION_CHANGE_ERROR or 
              packet_type == CLUSTER_SERVER_PACKET_T.IMAGE_CREATION_ERROR or
              packet_type == CLUSTER_SERVER_PACKET_T.IMAGE_EDITION_ERROR or
              packet_type == CLUSTER_SERVER_PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR or
              packet_type == CLUSTER_SERVER_PACKET_T.AUTO_DEPLOY_ERROR) :
            result["ErrorDescription"] = p.readInt()        
            result["CommandID"] = p.readString()                       
        return result