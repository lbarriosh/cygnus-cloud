# -*- coding: UTF8 -*-
'''
Definiciones del gestor de comandos
@author: Luis Barrios Hernández
@version: 1.5
'''

from ccutils.enums import enum

COMMAND_TYPE = enum("REGISTER_VM_SERVER", "UNREGISTER_OR_SHUTDOWN_VM_SERVER", "BOOTUP_VM_SERVER", 
                     "VM_BOOT_REQUEST", "HALT", "DESTROY_DOMAIN", "VM_SERVER_CONFIGURATION_CHANGE", "DEPLOY_IMAGE", "DELETE_IMAGE",
                     "CREATE_IMAGE", "EDIT_IMAGE", "DELETE_IMAGE_FROM_INFRASTRUCTURE", "AUTO_DEPLOY_IMAGE")

COMMAND_OUTPUT_TYPE = enum("VM_SERVER_REGISTRATION_ERROR", "VM_SERVER_BOOTUP_ERROR", 
                           "VM_CONNECTION_DATA", "VM_BOOT_FAILURE", "VM_SERVER_UNREGISTRATION_ERROR",
                           "VM_SERVER_SHUTDOWN_ERROR", "DOMAIN_DESTRUCTION_ERROR", "VM_SERVER_CONFIGURATION_CHANGE_ERROR",
                           "CONNECTION_ERROR", "COMMAND_TIMED_OUT", "IMAGE_DEPLOYMENT_ERROR", "DELETE_IMAGE_FROM_SERVER_ERROR",
                           "IMAGE_CREATION_ERROR", "IMAGE_EDITION_ERROR", "DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR",
                           "AUTO_DEPLOY_ERROR", "VM_SERVER_INTERNAL_ERROR", "IMAGE_DEPLOYED", "IMAGE_CREATED", "IMAGE_EDITED")

from clusterServer.networking.packets import CLUSTER_SERVER_PACKET_T as PACKET_T

class CommandsHandler(object):
    """
    Esta clase define métodos estáticos que serializan y deserializan comandos y salidas de comandos
    """
    
    def __init__(self, codesTranslator):
        self.__codesTranslator = codesTranslator
        
    def createAutoDeploymentCommand(self, imageID, instances):
        args = "{0}${1}".format(imageID, instances)
        return (COMMAND_TYPE.AUTO_DEPLOY_IMAGE, args)
        
    def createDeleteImageFromInfrastructureCommand(self, imageID):
        args = str(imageID)
        return (COMMAND_TYPE.DELETE_IMAGE_FROM_INFRASTRUCTURE, args)
        
    def createImageEditionCommand(self, create, imageID, userID):
        args = "{0}${1}".format(imageID, userID)
        if (create) :
            return (COMMAND_TYPE.CREATE_IMAGE, args)
        else :
            return (COMMAND_TYPE.EDIT_IMAGE, args)
        
    def createImageDeploymentCommand(self, deploy, serverNameOrIPAddress, imageID):
        args = "{0}${1}".format(serverNameOrIPAddress, imageID)
        if (deploy) :
            return (COMMAND_TYPE.DEPLOY_IMAGE, args)
        else :
            return (COMMAND_TYPE.DELETE_IMAGE, args)
    
    def createVMServerRegistrationCommand(self, vmServerIP, vmServerPort, vmServerName, isVanillaServer):
        """
        Crea un comando de registro de un servidor de máquinas virtuales
        Args:
            vmServerIP: la IP del servidor
            vmServerPort: el puerto en el que escucha
            vmServerName: el nombre del servidor
            isVanillaServer: indica si el servidor se usará preferentemente para editar imágenes vanilla
                o no.
        Devuelve:
            Una tupla (tipo de comando, argumentos) con el tipo del comando y sus argumentos serializados
        """
        args = "{0}${1}${2}${3}".format(vmServerIP, vmServerPort, vmServerName, isVanillaServer)
        return (COMMAND_TYPE.REGISTER_VM_SERVER, args)
    
    def createVMServerUnregistrationOrShutdownCommand(self, unregister, vmServerNameOrIP, isShutDown):
        """
        Crea un comando de borrado o apagado de un servidor de máquinas virtuales
        Args:
            unregister: indica si hay que borrar o no el servidor de máquinas virtuales
            vmServerNameOrIP: el nombre o la IP del servidor
            isShutDown: si es True, el servidor se cargará todas las máquinas de los usuarios en cuanto
            reciba el paquete. Si es False, esperará a que los usuarios terminen con ellas.
        Devuelve:
            Una tupla (tipo de comando, argumentos) con el tipo del comando y sus argumentos serializados
        """
        args =  "{0}${1}${2}".format(unregister, vmServerNameOrIP, isShutDown)
        return (COMMAND_TYPE.UNREGISTER_OR_SHUTDOWN_VM_SERVER, args)
    
    def createVMServerConfigurationChangeCommand(self, serverNameOrIPAddress, newName, newIPAddress, newPort, newVanillaImageEditionBehavior):
        args = "{0}${1}${2}${3}${4}".format(serverNameOrIPAddress, newName, newIPAddress, newPort, newVanillaImageEditionBehavior)
        return (COMMAND_TYPE.VM_SERVER_CONFIGURATION_CHANGE, args)
    
    def createVMServerBootCommand(self, vmServerNameOrIP):
        """
        Crea un comando de arranque de un servidor de máquinas virtuales
        Args:
            vmServerNameOrIP: el nombre o la IP del servidor
        Devuelve:
            Una tupla (tipo de comando, argumentos) con el tipo del comando y sus argumentos serializados
        """
        args = vmServerNameOrIP
        return (COMMAND_TYPE.BOOTUP_VM_SERVER, args)
    
    def createVMBootCommand(self, imageID, ownerID):
        """
        Crea un comando de arranque de una máquina virtual
        Args:
            imageID: el identificador único de la imagen
            ownerID: el identificador único del propietario de la imagen
        Devuelve:
            Una tupla (tipo de comando, argumentos) con el tipo del comando y sus argumentos serializados
        """
        args = "{0}${1}".format(imageID, ownerID)
        return (COMMAND_TYPE.VM_BOOT_REQUEST, args)
    
    def createHaltCommand(self, haltVMServers): 
        """
        Crea un comando que para toda la infraestructura
        Args:
            haltVMServers: si es True, el servidor se cargará todas las máquinas de los usuarios en cuanto
            reciba el paquete. Si es False, esperará a que los usuarios terminen con ellas.
        Devuelve:
            Una tupla (tipo de comando, argumentos) con el tipo del comando y sus argumentos serializados
        """
        return (COMMAND_TYPE.HALT, str(haltVMServers))
    
    def createDomainDestructionCommand(self, domainID):
        """
        Crea un comando de destrucción de un dominio
        Argumentos:
            domainID: el identificador único del dominio que hay que destruir
        Devuelve:
            Una tupla (tipo de comando, argumentos) con el tipo del comando y sus argumentos serializados
        """
        return (COMMAND_TYPE.DESTROY_DOMAIN, domainID)

    def deserializeCommandArgs(self, commandType, commandArgs):
        """
        Deserializa los argumentos de un comando
        Args:
            commandType: tipo de comando
            commandArgs: un string con los argumentos del comando
        Returns:
            un diccionario con los argumentos del comando (deserializados)
        """
        l = commandArgs.split("$")
        result = dict()
        if (commandType == COMMAND_TYPE.REGISTER_VM_SERVER) :
            result["VMServerIP"] = l[0]
            result["VMServerPort"] = int(l[1])
            result["VMServerName"] = l[2]
            result["IsVanillaServer"] = l[3] == "True"
        elif (commandType == COMMAND_TYPE.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
            result["Unregister"] = l[0] == 'True'
            result["VMServerNameOrIP"] = l[1]
            result["Halt"] = l[2] == 'True'
        elif (commandType == COMMAND_TYPE.BOOTUP_VM_SERVER) :
            result["VMServerNameOrIP"] = l[0]
        elif (commandType == COMMAND_TYPE.VM_BOOT_REQUEST) :
            result["VMID"] = int(l[0])
            result["UserID"] = int(l[1])
        elif (commandType == COMMAND_TYPE.HALT) :
            result["HaltVMServers"] = l[0] == 'True'
        elif (commandType == COMMAND_TYPE.DESTROY_DOMAIN):
            result["DomainID"] = l[0]
        elif (commandType == COMMAND_TYPE.VM_SERVER_CONFIGURATION_CHANGE) :
            result["VMServerNameOrIPAddress"] = l[0]
            result["NewServerName"] = l[1]
            result["NewServerIPAddress"] = l[2]
            result["NewServerPort"] = int(l[3])
            result["NewVanillaImageEditionBehavior"] = l[4] == "True"
        elif (commandType == COMMAND_TYPE.DEPLOY_IMAGE or
              commandType == COMMAND_TYPE.DELETE_IMAGE):
            result["VMServerNameOrIPAddress"] = l[0]
            result["ImageID"] = int(l[1])
        elif (commandType == COMMAND_TYPE.CREATE_IMAGE or
              commandType == COMMAND_TYPE.EDIT_IMAGE):
            result["ImageID"] = int(l[0])
            result["OwnerID"] = int(l[1])
        elif (commandType == COMMAND_TYPE.DELETE_IMAGE_FROM_INFRASTRUCTURE):
            result["ImageID"] = int(l[0])
        elif (commandType == COMMAND_TYPE.AUTO_DEPLOY_IMAGE):
            result["ImageID"] = int(l[0])
            result["MaxInstances"] = int(l[1])
        return result
    
    def __getErrorOutputType(self, packet_type):
        if (packet_type == PACKET_T.VM_SERVER_REGISTRATION_ERROR) :
            return COMMAND_OUTPUT_TYPE.VM_SERVER_REGISTRATION_ERROR
        elif (packet_type == PACKET_T.VM_SERVER_BOOTUP_ERROR) :
            return COMMAND_OUTPUT_TYPE.VM_SERVER_BOOTUP_ERROR
        elif (packet_type == PACKET_T.VM_BOOT_FAILURE) :
            return COMMAND_OUTPUT_TYPE.VM_BOOT_FAILURE
        elif (packet_type == PACKET_T.VM_SERVER_SHUTDOWN_ERROR):
            return COMMAND_OUTPUT_TYPE.VM_SERVER_SHUTDOWN_ERROR
        elif (packet_type == PACKET_T.VM_SERVER_UNREGISTRATION_ERROR):
            return COMMAND_OUTPUT_TYPE.VM_SERVER_UNREGISTRATION_ERROR
        elif (packet_type == PACKET_T.DOMAIN_DESTRUCTION_ERROR):
            return COMMAND_OUTPUT_TYPE.DOMAIN_DESTRUCTION_ERROR
        elif (packet_type == PACKET_T.VM_SERVER_CONFIGURATION_CHANGE_ERROR):
            return COMMAND_OUTPUT_TYPE.VM_SERVER_CONFIGURATION_CHANGE_ERROR
        elif (packet_type == PACKET_T.IMAGE_DEPLOYMENT_ERROR):
            return COMMAND_OUTPUT_TYPE.IMAGE_DEPLOYMENT_ERROR
        elif (packet_type == PACKET_T.DELETE_IMAGE_FROM_SERVER_ERROR):
            return COMMAND_OUTPUT_TYPE.DELETE_IMAGE_FROM_SERVER_ERROR
        elif (packet_type == PACKET_T.IMAGE_CREATION_ERROR):
            return COMMAND_OUTPUT_TYPE.IMAGE_CREATION_ERROR
        elif (packet_type == PACKET_T.IMAGE_EDITION_ERROR):
            return COMMAND_OUTPUT_TYPE.IMAGE_EDITION_ERROR
        elif (packet_type == PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR):
            return COMMAND_OUTPUT_TYPE.DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR
        elif (packet_type == PACKET_T.AUTO_DEPLOY_ERROR):
            return COMMAND_OUTPUT_TYPE.AUTO_DEPLOY_ERROR
        elif (packet_type == PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR):
            return COMMAND_OUTPUT_TYPE.DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR
        else :
            return COMMAND_OUTPUT_TYPE.VM_SERVER_INTERNAL_ERROR
    
    def createErrorOutput(self, packet_type, errorCode):
        """
        Crea salidas de error para los comandos de arranque, apagado y borrado
        de servidores de máquinas virtuales
        Args:
            serverNameOrIPAddress: el nomrbe o la IP del servidor
            errorMessage: un mensaje de error
        Devuelve:
            Una tupla (tipo de salida, salida del comando) con el tipo de la salida del comando y su contenido serializado
        """
        return (self.__getErrorOutputType(packet_type), self.__codesTranslator.translateErrorDescriptionCode(errorCode))
    
    def deserializeCommandOutput(self, commandOutputType, content):
        """
        Deserializa la salida de un comando
        Args:
            commandType: el tipo de la salida del comando.
            commandArgs: la salida del comando serializada
        Returns:
            Un diccionario con la salida del comando deserializada
        """
        l = content.split("$")
        result = dict()
        result["OutputType"] = commandOutputType
        if (commandOutputType == COMMAND_OUTPUT_TYPE.VM_CONNECTION_DATA): 
            result["VNCServerIPAddress"] = l[0]
            result["VNCServerPort"] = int(l[1])
            result["VNCServerPassword"] = l[2]
        else :
            result["ErrorMessage"] = l[0]              
        return result
    
    def createConnectionErrorOutput(self):
        return (COMMAND_OUTPUT_TYPE.CONNECTION_ERROR, "No se puede establecer la conexión con el servidor de cluster")