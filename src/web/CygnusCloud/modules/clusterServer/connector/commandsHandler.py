# -*- coding: UTF8 -*-
'''
Command handler class definition.
@author: Luis Barrios Hernández
@version: 1.0
'''

from ccutils.enums import enum

COMMAND_TYPE = enum("REGISTER_VM_SERVER", "UNREGISTER_OR_SHUTDOWN_VM_SERVER", "BOOTUP_VM_SERVER", 
                     "VM_BOOT_REQUEST", "HALT")

COMMAND_OUTPUT_TYPE = enum("VM_SERVER_REGISTRATION_ERROR", "VM_SERVER_BOOTUP_ERROR", 
                           "VM_CONNECTION_DATA", "VM_BOOT_FAILURE", "VM_SERVER_UNREGISTRATION_ERROR",
                           "VM_SERVER_SHUTDOWN_ERROR")

from clusterServer.networking.packets import MAIN_SERVER_PACKET_T as PACKET_T

class CommandsHandler(object):
    """
    This class provides methods to serialize and deserialize commands and command outputs. 
    """
    
    @staticmethod
    def createVMServerRegistrationCommand(vmServerIP, vmServerPort, vmServerName):
        """
        Creates a virtual machine server registration command
        Args:
            vmServerIP: the virtual machine server's IPv4 address
            vmServerPort: the virtual machine server's listenning port
            vmServerName: the virtual machine server's name.
        Returns:
            A tuple (command type, command arguments) containing the command type and its serialized arguments.
        """
        args = "{0}${1}${2}".format(vmServerIP, vmServerPort, vmServerName)
        return (COMMAND_TYPE.REGISTER_VM_SERVER, args)
    
    @staticmethod
    def createVMServerUnregistrationOrShutdownCommand(unregister, vmServerNameOrIP, halt):
        """
        Creates a virtual machine server unregistration or shutdown command
        Args:
            unregister: if True, the virtual machine server will be deleted from the system.
            If false, it will only be shut down.
            vmServerNameOrIP: the virtual machine server's name or IPv4 address
            halt: if True, the virtual machine server will destroy all the active virtual machines and terminate.
            If False, the virtual machine will wait for all the virtual machines to terminate, and then it will
            shut down.
        Returns:
            A tuple (command type, command arguments) containing the command type and its serialized arguments.
        """
        args =  "{0}${1}${2}".format(unregister, vmServerNameOrIP, halt)
        return (COMMAND_TYPE.UNREGISTER_OR_SHUTDOWN_VM_SERVER, args)
    
    @staticmethod
    def createVMServerBootCommand(vmServerNameOrIP):
        """
        Creates a virtual machine server boot command
        Args:
            vmServerNameOrIP: the virtual machine server's name or IPv4 address.
        Returns:
            A tuple (command type, command arguments) containing the command type and its serialized arguments.
        """
        args = vmServerNameOrIP
        return (COMMAND_TYPE.BOOTUP_VM_SERVER, args)
    
    @staticmethod
    def createVMBootCommand(vmID, userID):
        """
        Creates a virtual machine boot command
        Args:
            vmID: the virtual machine's unique identifier.
            userID: the user's unique identifier.
        Returns:
            A tuple (command type, command arguments) containing the command type and its serialized arguments.
        """
        args = "{0}${1}".format(vmID, userID)
        return (COMMAND_TYPE.VM_BOOT_REQUEST, args)
    
    @staticmethod
    def createHaltCommand(haltVMServers): 
        """
        Creates an infrastructure HALT command
        Args:
            haltVMServers: if True, the virtual machine servers will be immediately shut down. If false,
            they will be shut down when they'll have no active virtual machines.
        Returns:
            A tuple (command type, command arguments) containing the command type and its serialized arguments.
        """
        return (COMMAND_TYPE.HALT, str(haltVMServers))

    @staticmethod
    def deserializeCommandArgs(commandType, commandArgs):
        """
        Deserializes a command's argument.
        Args:
            commandType: the command's type.
            commandArgs: the command's args.
        Returns:
            a dictionary containing the command arguments.    
        """
        l = commandArgs.split("$")
        result = dict()
        if (commandType == COMMAND_TYPE.REGISTER_VM_SERVER) :
            result["VMServerIP"] = l[0]
            result["VMServerPort"] = int(l[1])
            result["VMServerName"] = l[2]
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
        return result
    
    @staticmethod
    def createVMServerGenericErrorOutput(packet_type, serverNameOrIPAddress, errorMessage):
        """
        Creates a virtual machine server boot up, unregistration or shutdown error command output.
        Args:
            serverNameOrIPAddress: the virtual machine server's name or IP address
            errorMessage: an error message
        Returns:
            A tuple (command output type, command output) containing the command output's type and its serialized content.
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
        Creates a virtual machine server registration error command output.
        Args:
            serverNameOrIPAddress: the virtual machine server's name or IP address
            errorMessage: an error message
        Returns:
            A tuple (command output type, command output) containing the command output's type and its serialized content.
        """
        content = "{0}${1}${2}${3}".format(vmServerIP, vmServerPort, vmServerName, errorMessage)
        return (COMMAND_OUTPUT_TYPE.VM_SERVER_REGISTRATION_ERROR, content)
    
    @staticmethod
    def createVMBootFailureErrorOutput(vmID, errorMessage):
        """
        Creates a virtual machine boot up error command output.
        Args:
            serverNameOrIPAddress: the virtual machine server's name or IP address
            errorMessage: an error message
        Returns:
            A tuple (command output type, command output) containing the command output's type and its serialized content.
        """
        content = "{0}${1}".format(vmID, errorMessage)
        return (COMMAND_OUTPUT_TYPE.VM_BOOT_FAILURE, content)
    
    @staticmethod
    def createVMConnectionDataOutput(vncServerIPAddress, vncServerPort, vncServerPassword):
        """
        Creates a virtual machine boot up command output that contains the connection parameters.
        Args:
            vncServerIPAddress: the VNC server's IP address
            vncServerPort: the VNC server's port
            vncServerPassword: the VNC server's password
        Returns:
            A tuple (command output type, command output) containing the command output's type and its serialized content.
        """
        content = "{0}${1}${2}".format(vncServerIPAddress, vncServerPort, vncServerPassword)
        return (COMMAND_OUTPUT_TYPE.VM_CONNECTION_DATA, content)
    
    @staticmethod
    def deserializeCommandOutput(commandOutputType, content):
        """
        Deserializes a command's argument.
        Args:
            commandType: the command's type.
            commandArgs: the command's args.
        Returns:
            A dictionary containing the command's output
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
            
        return result