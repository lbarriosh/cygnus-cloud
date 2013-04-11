# -*- coding: UTF8 -*-
'''
Definiciones del gestor de comandos
@author: Luis Barrios Hernández
@version: 1.5
'''

from ccutils.enums import enum

COMMAND_TYPE = enum("REGISTER_VM_SERVER", "UNREGISTER_OR_SHUTDOWN_VM_SERVER", "BOOTUP_VM_SERVER", 
                     "VM_BOOT_REQUEST", "HALT", "DESTROY_DOMAIN", "VM_SERVER_CONFIGURATION_CHANGE")

COMMAND_OUTPUT_TYPE = enum("VM_SERVER_REGISTRATION_ERROR", "VM_SERVER_BOOTUP_ERROR", 
                           "VM_CONNECTION_DATA", "VM_BOOT_FAILURE", "VM_SERVER_UNREGISTRATION_ERROR",
                           "VM_SERVER_SHUTDOWN_ERROR", "DOMAIN_DESTRUCTION_ERROR", "VM_SERVER_CONFIGURATION_CHANGE_ERROR",
                           "CONNECTION_ERROR")

from clusterServer.networking.packets import MAIN_SERVER_PACKET_T as PACKET_T

class CommandsHandler(object):
    """
    Esta clase define métodos estáticos que serializan y deserializan comandos y salidas de comandos
    """
    
    @staticmethod
    def createVMServerRegistrationCommand(vmServerIP, vmServerPort, vmServerName, isVanillaServer):
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
    
    @staticmethod
    def createVMServerUnregistrationOrShutdownCommand(unregister, vmServerNameOrIP, isShutDown):
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
    
    @staticmethod
    def createVMServerConfigurationChangeCommand(serverNameOrIPAddress, newName, newIPAddress, newPort, newVanillaImageEditionBehavior):
        args = "{0}${1}${2}${3}${4}".format(serverNameOrIPAddress, newName, newIPAddress, newPort, newVanillaImageEditionBehavior)
        return (COMMAND_TYPE.VM_SERVER_CONFIGURATION_CHANGE, args)
    
    @staticmethod
    def createVMServerBootCommand(vmServerNameOrIP):
        """
        Crea un comando de arranque de un servidor de máquinas virtuales
        Args:
            vmServerNameOrIP: el nombre o la IP del servidor
        Devuelve:
            Una tupla (tipo de comando, argumentos) con el tipo del comando y sus argumentos serializados
        """
        args = vmServerNameOrIP
        return (COMMAND_TYPE.BOOTUP_VM_SERVER, args)
    
    @staticmethod
    def createVMBootCommand(imageID, ownerID):
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
    
    @staticmethod
    def createHaltCommand(haltVMServers): 
        """
        Crea un comando que para toda la infraestructura
        Args:
            haltVMServers: si es True, el servidor se cargará todas las máquinas de los usuarios en cuanto
            reciba el paquete. Si es False, esperará a que los usuarios terminen con ellas.
        Devuelve:
            Una tupla (tipo de comando, argumentos) con el tipo del comando y sus argumentos serializados
        """
        return (COMMAND_TYPE.HALT, str(haltVMServers))
    
    @staticmethod
    def createDomainDestructionCommand(domainID):
        """
        Crea un comando de destrucción de un dominio
        Argumentos:
            domainID: el identificador único del dominio que hay que destruir
        Devuelve:
            Una tupla (tipo de comando, argumentos) con el tipo del comando y sus argumentos serializados
        """
        return (COMMAND_TYPE.DESTROY_DOMAIN, domainID)

    @staticmethod
    def deserializeCommandArgs(commandType, commandArgs):
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
        return result
    
    @staticmethod
    def createVMServerGenericErrorOutput(packet_type, serverNameOrIPAddress, errorMessage):
        """
        Crea salidas de error para los comandos de arranque, apagado y borrado
        de servidores de máquinas virtuales
        Args:
            serverNameOrIPAddress: el nomrbe o la IP del servidor
            errorMessage: un mensaje de error
        Devuelve:
            Una tupla (tipo de salida, salida del comando) con el tipo de la salida del comando y su contenido serializado
        """
        content = "{0}${1}".format(serverNameOrIPAddress, errorMessage)
        if (packet_type == PACKET_T.VM_SERVER_BOOTUP_ERROR) :
            outputType = COMMAND_OUTPUT_TYPE.VM_SERVER_BOOTUP_ERROR
        elif (packet_type == PACKET_T.VM_SERVER_UNREGISTRATION_ERROR) :
            outputType = COMMAND_OUTPUT_TYPE.VM_SERVER_UNREGISTRATION_ERROR
        else :
            outputType = COMMAND_OUTPUT_TYPE.VM_SERVER_SHUTDOWN_ERROR
        return (outputType, content)
    
    @staticmethod
    def createVMServerRegistrationErrorOutput(vmServerIP, vmServerPort, vmServerName, errorMessage):
        """
        Crea salidas de error para los comandos de registro de servidores de máquinas virtuales
        Args:
            vmServeriP: la IP del servidor
            vmServerPort: el puerto en el que el serivodr escucha
            vmServerName: el nombre del servidor
            errorMessage: un mensaje de error
        Devuelve:
            Una tupla (tipo de salida, salida del comando) con el tipo de la salida del comando y su contenido serializado
        """
        content = "{0}${1}${2}${3}".format(vmServerIP, vmServerPort, vmServerName, errorMessage)
        return (COMMAND_OUTPUT_TYPE.VM_SERVER_REGISTRATION_ERROR, content)
    
    @staticmethod
    def createVMBootFailureErrorOutput(imageID, errorMessage):
        """
        Crea salidas de error para los comandos de arranque de máquinas virtuales
        Args:
            imageID: el identificador único de la imagen
            errorMessage: un mensaje de error
        Devuelve:
            Una tupla (tipo de salida, salida del comando) con el tipo de la salida del comando y su contenido serializado
        """
        content = "{0}${1}".format(imageID, errorMessage)
        return (COMMAND_OUTPUT_TYPE.VM_BOOT_FAILURE, content)
    
    @staticmethod
    def createVMConnectionDataOutput(vncServerIPAddress, vncServerPort, vncServerPassword):
        """
        Crea la salida normal para los comandos de arranque de una máquina virtual. Esta contiene los datos de conexión.
        Args:
            vncServerIPAddress: la IP del servidor VNC
            vncServerPort: el puerto del servidor VNC
            vncServerPassword: la contraseña del servidor VNC
        Devuelve:
            Una tupla (tipo de salida, salida del comando) con el tipo de la salida del comando y su contenido serializado
        """
        content = "{0}${1}${2}".format(vncServerIPAddress, vncServerPort, vncServerPassword)
        return (COMMAND_OUTPUT_TYPE.VM_CONNECTION_DATA, content)
    
    @staticmethod
    def createDomainDestructionErrorOutput(errorMessage):
        """
        Crea un mensaje de error asociado a la destrucción de una máquina virtual
        Argumentos:
            errorMessage: el mensaje de error
        Devuelve:
            Una tupla (tipo de salida, salida del comando) con el tipo de la salida del comando y su contenido serializado
        """
        return (COMMAND_OUTPUT_TYPE.DOMAIN_DESTRUCTION_ERROR, errorMessage)
    
    @staticmethod
    def createVMServerConfigurationChangeErrorOutput(reason):
        return (COMMAND_OUTPUT_TYPE.VM_SERVER_CONFIGURATION_CHANGE_ERROR, reason)
    
    @staticmethod
    def createConnectionErrorOutput():
        return (COMMAND_OUTPUT_TYPE.CONNECTION_ERROR, "The connection was lost")
    
    @staticmethod
    def deserializeCommandOutput(commandOutputType, content):
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
        if (commandOutputType == COMMAND_OUTPUT_TYPE.VM_SERVER_BOOTUP_ERROR or
            commandOutputType == COMMAND_OUTPUT_TYPE.VM_SERVER_SHUTDOWN_ERROR or
            commandOutputType == COMMAND_OUTPUT_TYPE.VM_SERVER_UNREGISTRATION_ERROR) :
            result["ServerNameOrIPAddress"] = l[0]
            result["ErrorMessage"] = l[1]
        elif (commandOutputType == COMMAND_OUTPUT_TYPE.VM_SERVER_REGISTRATION_ERROR) :
            result["VMServerIP"] = l[0]
            result["VMServerPort"] = l[1]
            result["VMServerName"] = l[2]
            result["ErrorMessage"] = l[3]
        elif (commandOutputType == COMMAND_OUTPUT_TYPE.VM_BOOT_FAILURE) :
            result["VMID"] = int(l[0])
            result["ErrorMessage"] = l[1]
        elif (commandOutputType == COMMAND_OUTPUT_TYPE.VM_CONNECTION_DATA): 
            result["VNCServerIPAddress"] = l[0]
            result["VNCServerPort"] = int(l[1])
            result["VNCServerPassword"] = l[2]
        elif (commandOutputType == COMMAND_OUTPUT_TYPE.DOMAIN_DESTRUCTION_ERROR or
              commandOutputType == COMMAND_OUTPUT_TYPE.VM_SERVER_CONFIGURATION_CHANGE_ERROR or
              commandOutputType == COMMAND_OUTPUT_TYPE.CONNECTION_ERROR) :
            result["ErrorMessage"] = l[0]
            
        return result