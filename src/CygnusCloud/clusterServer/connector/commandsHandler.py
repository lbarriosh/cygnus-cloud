# -*- coding: UTF8 -*-
'''
Command handler definition.
@author: Luis Barrios Hernández
@version: 1.0
'''

from ccutils.enums import enum

COMMAND_TYPE = enum("REGISTER_VM_SERVER", "UNREGISTER_OR_SHUTDOWN_VM_SERVER", "BOOTUP_VM_SERVER", 
                     "VM_BOOT_REQUEST", "HALT")

COMMAND_OUTPUT_TYPE = enum("VM_SERVER_REGISTRATION_ERROR", "VM_SERVER_BOOTUP_ERROR", 
                           "VM_CONNECTION_DATA", "VM_BOOT_FAILURE")

class CommandsHandler(object):
    
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
    def createVMServerUnregistrationCommand(unregister, vmServerNameOrIP, halt):
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
        return (COMMAND_TYPE.HALT, "")

    @staticmethod
    def deserializeCommandArgs(commandType, commandArgs):
        """
        Deserializes a command's argument.
        Args:
            commandType: the command's type.
            commandArgs: the command's args.
        Returns:
            A tuple (command type, command arguments) containing the command type and its serialized arguments.    
        """
        l = commandArgs.split("$")
        result = dict()
        if (commandType == COMMAND_TYPE.REGISTER_VM_SERVER) :
            result["VMServerIP"] = l[0]
            result["VMServerPort"] = int(l[1])
            result["VMServerName"] = l[2]
        elif (commandType == COMMAND_TYPE.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
            result["Unregister"] = bool(l[0])
            result["VMServerNameOrIP"] = l[1]
            result["Halt"] = bool(l[2])
        elif (commandType == COMMAND_TYPE.BOOTUP_VM_SERVER) :
            result["VMServerNameOrIP"] = l[0]
        elif (commandType == COMMAND_TYPE.VM_BOOT_REQUEST) :
            result["VMID"] = int(l[0])
            result["UserID"] = int(l[1])
        elif (commandType == COMMAND_TYPE.HALT) :
            result["HaltVMServers"] = bool(l[0])
        return result
    
    @staticmethod
    def createVMServerBootUpErrorOutput(serverNameOrIPAddress, errorMessage):
        """
        Creates a virtual machine server boot up error command output.
        Args:
            serverNameOrIPAddress: the virtual machine server's name or IP address
            errorMessage: an error message
        """
        args = "{0}${1}".format(serverNameOrIPAddress, errorMessage)
        return (COMMAND_OUTPUT_TYPE.VM_SERVER_BOOTUP_ERROR, args)
    
    @staticmethod
    def createVMServerRegistrationErrorOutput(serverNameOrIPAddress, errorMessage):
        """
        Creates a virtual machine server registration error command output.
        Args:
            serverNameOrIPAddress: the virtual machine server's name or IP address
            errorMessage: an error message
        """
        args = "{0}${1}".format(serverNameOrIPAddress, errorMessage)
        return (COMMAND_OUTPUT_TYPE.VM_SERVER_REGISTRATION_ERROR, args)
    
    @staticmethod
    def createVMBootFailureErrorOutput(vmID, userID, errorMessage):
        """
        Creates a virtual machine boot up error command output.
        Args:
            serverNameOrIPAddress: the virtual machine server's name or IP address
            errorMessage: an error message
        """
        args = "{0}${1}${2}".format(vmID, userID, errorMessage)
        return (COMMAND_OUTPUT_TYPE.VM_BOOT_FAILURE, args)
    
    @staticmethod
    #def createVMConnectionDataOutput():
    # TODO: check if the vm connection data packets contain the user ID or not
    # TODO. create the command output deserializer

#          
#         
#            self.__callback.handleVMConnectionData(data["UserID"], data["VNCServerIPAddress"], data["VNCServerPort"],
#                                                   data["VNCServerPassword"])