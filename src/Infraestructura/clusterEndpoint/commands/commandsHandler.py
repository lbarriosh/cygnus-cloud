# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: commandsHandler.py    
    Version: 5.0
    Description: commands handler definition
    
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
from clusterEndpoint.commands.command_type import COMMAND_TYPE
from clusterEndpoint.commands.command_output_type import COMMAND_OUTPUT_TYPE
from clusterServer.packetHandling.packet_t import CLUSTER_SERVER_PACKET_T as PACKET_T

class CommandsHandler(object):
    """
    These class provides methods to serialize and deserialize commands and their outputs.
    """
    
    def __init__(self, codesTranslator):
        """
        Initializes the handler's state
        Args:
            codesTranslator: the codes translator object to use
        """
        self.__codesTranslator = codesTranslator
        
    def createAutoDeploymentCommand(self, imageID, instances):
        """
        Creates an image auto-deployment command
        Args:
            imageID: the affected image's ID
            instances: the number of instances to be allocated
        Returns:
            A tuple (command type, serialized command args)
        """
        args = "{0}${1}".format(imageID, instances)
        return (COMMAND_TYPE.AUTO_DEPLOY_IMAGE, args)
        
    def createDeleteImageFromInfrastructureCommand(self, imageID):
        """
        Creates a total image deletion command
        Args:
            imageID: the affected image's ID
        Returns:
            A tuple (command type, serialized command args)
        """
        args = str(imageID)
        return (COMMAND_TYPE.DELETE_IMAGE_FROM_INFRASTRUCTURE, args)
    
    def createImageAdditionCommand(self, userID, baseImageID, imageName, imageDescription):
        """
        Creates an image addition command
        Args:
            userID: the image owner's ID
            baseImageID: the base image's ID
            imageName: the new image's name
            imageDescription: the new image's description
        Returns:
            A tuple (command type, serialized command args)
        """
        args = "{0}${1}${2}${3}".format(userID, baseImageID, imageName, imageDescription)
        return (COMMAND_TYPE.CREATE_IMAGE, args)
        
    def createImageEditionCommand(self, imageID, userID):
        """
        Creates an image edition command
        Args:
            imageID: the affected image's ID
            userID: the image owner's ID
        Returns:
            A tuple (command type, serialized command args)
        """
        args = "{0}${1}".format(imageID, userID)
        return (COMMAND_TYPE.EDIT_IMAGE, args)            
        
    def createImageDeploymentCommand(self, deploy, serverNameOrIPAddress, imageID):
        """
        Creates a manual image deployment or a manual image deletion command
        Args:
            deploy: if it's True, an image deployment command will be created. If it's False,
                an image deletion command will be created.
            serverNameOrIPAddress: the host's name or IP address
            imageID: the affected image's ID
        Returns:
            A tuple (command type, serialized command args)
        """
        args = "{0}${1}".format(serverNameOrIPAddress, imageID)
        if (deploy) :
            return (COMMAND_TYPE.DEPLOY_IMAGE, args)
        else :
            return (COMMAND_TYPE.DELETE_IMAGE, args)
    
    def createVMServerRegistrationCommand(self, vmServerIP, vmServerPort, vmServerName, isEditionServer):
        """
        Creates a virtual machine server registration command
        Args:
            vmServerIP: the new virtual machine server's IP address
            vmServerPort: the new virtual machine server's listenning port
            vmServerName: the new virtual machine server's name
            isEditionServer: indicates if the virtual machine server will be used to create and edit 
                images or not
        Returns:
            A tuple (command type, serialized command args)
        """
        args = "{0}${1}${2}${3}".format(vmServerIP, vmServerPort, vmServerName, isEditionServer)
        return (COMMAND_TYPE.REGISTER_VM_SERVER, args)
    
    def createVMServerUnregistrationOrShutdownCommand(self, unregister, vmServerNameOrIP, isShutDown):
        """
        Creates a virtual machine server unregistration or shutdown command
        Args:
            unregister: if it's True, an virtual machine server unregistration command will be created. If it's False,
                a virtual machine server shutdown command will be created.
            vmServerNameOrIPAddress: the virtual machine server's name or IPv4 address
            isShutDown: indicates if the virtual machine server must be shut down
        Returns:
            A tuple (command type, serialized command args)
        """
        args =  "{0}${1}${2}".format(unregister, vmServerNameOrIP, isShutDown)
        return (COMMAND_TYPE.UNREGISTER_OR_SHUTDOWN_VM_SERVER, args)
    
    def createVMServerConfigurationChangeCommand(self, serverNameOrIPAddress, newName, newIPAddress, newPort, newImageEditionBehavior):
        """
        Creates a virtual machine server configuration change command
        Args:
            serverNameOrIPAddress: the virtual machine server's name or IP address
            newName: the virtual machine server's new name
            newIPAddress: the virtual machine server's IP new address
            newPort: the virtual machine server's new port            
            newImageEditionBehavior: indicates if the virtual machine server will be used to create and edit 
                images or not
        Returns:
            A tuple (command type, serialized command args)
        """
        args = "{0}${1}${2}${3}${4}".format(serverNameOrIPAddress, newName, newIPAddress, newPort, newImageEditionBehavior)
        return (COMMAND_TYPE.VM_SERVER_CONFIGURATION_CHANGE, args)
    
    def createVMServerBootCommand(self, vmServerNameOrIP):
        """
        Creates a virtual machine server boot command
        Args:
            vmServerNameOrIP: the virtual machine server's name or IP address
        Returns:
            A tuple (command type, serialized command args)
        """
        args = vmServerNameOrIP
        return (COMMAND_TYPE.BOOTUP_VM_SERVER, args)
    
    def createVMBootCommand(self, imageID, ownerID):
        """
        Creates a virtual machine boot command
        Args:
            imageID: an image ID
            ownerID: the virtual machine owner's ID
        Returns:
            A tuple (command type, serialized command args)
        """
        args = "{0}${1}".format(imageID, ownerID)
        return (COMMAND_TYPE.VM_BOOT_REQUEST, args)
    
    def createHaltCommand(self, haltVMServers): 
        """
        Creates a HALT command
        Args:
            haltServers: indicates if the virtual machine servers must be shut down immediately or not
        Returns:
            A tuple (command type, serialized command args)
        """
        return (COMMAND_TYPE.HALT, str(haltVMServers))
    
    def createDomainDestructionCommand(self, domainID):
        """
        Creates a domain destruction command
        Args:
            domainID: the domain to be destructed ID
        Devuelve:
            A tuple (command type, serialized command args)
        """
        return (COMMAND_TYPE.DESTROY_DOMAIN, domainID)
    
    def createDomainRebootCommand(self, domainID):
        """
        Creates a domain reboot command
        Args:
            domainID: the domain to be rebooted ID
        Devuelve:
            A tuple (command type, serialized command args)
        """
        return (COMMAND_TYPE.REBOOT_DOMAIN, domainID)

    def deserializeCommandArgs(self, commandType, commandArgs):
        """
        Deserializes a command's arguments
        Args:
            commandType: the command's type
            commandArgs: the serialized command's arguments
        Returns:
            A dictionary containing the deserialized command arguments.
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
        elif (commandType == COMMAND_TYPE.DESTROY_DOMAIN or 
              commandType == COMMAND_TYPE.REBOOT_DOMAIN):
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
        elif (commandType == COMMAND_TYPE.CREATE_IMAGE):
            result["OwnerID"] = int(l[0])
            result["BaseImageID"] = int(l[1])
            result["ImageName"] = l[2]
            result["ImageDescription"] = l[3]
        elif (commandType == COMMAND_TYPE.EDIT_IMAGE) :
            result["ImageID"] = int(l[0])
            result["OwnerID"] = int(l[1])
        elif (commandType == COMMAND_TYPE.DELETE_IMAGE_FROM_INFRASTRUCTURE):
            result["ImageID"] = int(l[0])
        elif (commandType == COMMAND_TYPE.AUTO_DEPLOY_IMAGE):
            result["ImageID"] = int(l[0])
            result["MaxInstances"] = int(l[1])
        return result
    
    def __getErrorOutputType(self, packet_type):
        """
        Returns the error output type associated with an error packet type
        Args:
            packet_type: an error packet type
        Returns:
            the error output type associated with the given error packet type
        """
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
        elif (packet_type == PACKET_T.DOMAIN_REBOOT_ERROR):
            return COMMAND_OUTPUT_TYPE.DOMAIN_REBOOT_ERROR
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
        Creates a generic error command output
        Args:
            packet_type: a packet type
            errorCode: an error description code
        Returns:
            A tuple (command type, serialized command output)
        """
        return (self.__getErrorOutputType(packet_type), self.__codesTranslator.translateErrorDescriptionCode(errorCode))
    
    def createVMConnectionDataOutput(self, VNCServerIP, VNCServerPort, VNCServerPassword):
        """
        Creates a virtual machine connection data output
        Args:
            VNCServerIP: the VNC server's IP address
            VNCServerPort: the VNC server's port
            VNCServerPassword: the VNC server's password
        Returns:
            A tuple (command type, serialized command output)
        """
        output = "{0}${1}${2}".format(VNCServerIP, VNCServerPort, VNCServerPassword)
        return (COMMAND_OUTPUT_TYPE.VM_CONNECTION_DATA, output)
    
    def createConnectionErrorOutput(self):
        """
        Creates a connection error output
        Args:
            None
        Returns:
            A tuple (command type, serialized command output)
        """
        return (COMMAND_OUTPUT_TYPE.CONNECTION_ERROR, "No se puede establecer la conexión con el servidor de cluster")
    
    def deserializeCommandOutput(self, commandOutputType, content):
        """
        Deserializes a command's output
        Args:
            commandOutputType: a command output type
            commandArgs: the serialized command output
        Returns:
            A dictionary containing the command output's deserialized content.
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