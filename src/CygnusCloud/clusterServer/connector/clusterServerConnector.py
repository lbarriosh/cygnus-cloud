# -*- coding: utf8 -*-
'''
Cluster server connector definitions.
@author: Luis Barrios Hernández
@version: 2.2
'''
from database.systemStatusDB.systemStatusDBReader import SystemStatusDatabaseReader
from database.commands.commandsDatabaseConnector import CommandsDatabaseConnector
from clusterServer.connector.commandsHandler import CommandsHandler
from time import sleep

class ClusterServerConnector(object):
    """
    These objects communicate the website with the cluster server endpoint.
    """
    
    def __init__(self, userID):
        """
        Initializes the connector's state.
        Args:
            userID: an user's unique identifier. This INTEGER number will be used to identify
            the user's requests. 
        """
        self.__userID = userID
    
    def connectToDatabases(self, statusDBName, commandsDBName, databaseUser, databasePassword):
        """
        Establishes a connection with the status and command databases.
        Args:
            statusDBName: the status database's name
            commandsDBName: the command's database name
            databaseUser: the databases' user name
            databasePassword: the databases's user password
        Returns:
            Nothing
        """
        self.__statusDBConnector = SystemStatusDatabaseReader(databaseUser, databasePassword, statusDBName)
        self.__statusDBConnector.connect()
        self.__commandsDBConnector = CommandsDatabaseConnector(databaseUser, databasePassword, commandsDBName, 1)
        self.__commandsDBConnector.connect()
        
    def dispose(self):
        """
        Closes the database connections.
        Args:
            None
        Returns:
            Nothing
        @attention: To avoid potential data loss, this method MUST be called when the 
        website stops using the connnector.
        """
        self.__statusDBConnector.disconnect()
        self.__commandsDBConnector.disconnect()
        
    def getActiveVMsData(self):
        """
        Returns the active virtual machines' data.
        Args:
            None
        Returns: a list of dictionaries with the keys VMServerName, UserID, VMID, VMName, VNCPort
            and VNCPassword with their corresponding values.
        """
        return self.__statusDBConnector.getActiveVMsData()
    
    def getVMDistributionData(self):
        """
        Returns the image (a.k.a. available virtual machines) distribution data.
        Args:
            None
        Returns: a list of dictionaries with the keys VMServerName, VMID and the corresponding values
        """
        return self.__statusDBConnector.getVMDistributionData()
        
    def getVMServersData(self):
        """
        Returns the virtual machine server's basic data.
        Args:
            None
        Returns: a list of dictionaries with the keys VMServerName, VMServerStatus, VMServerIP,
            VMServerListenningPort and their corresponding values.
        """
        return self.__statusDBConnector.getVMServersData()
        
    def registerVMServer(self, vmServerIP, vmServerPort, vmServerName):
        """
        Registers a virtual machine server on the system
        Args:
            vmServerIP: the virtual machine server's IP address
            vmServerPort: the virtual machine server's port
            vmServerName: the virtual machine server's name
        Returns:
            A command ID.
            @attention: DO NOT rely on the command ID's internal representation: it can change without prior notice.
        """
        (commandType, commandArgs) = CommandsHandler.createVMServerRegistrationCommand(vmServerIP, vmServerPort, vmServerName)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
        
    def unregisterVMServer(self, vmServerNameOrIP, halt):
        """
        Unregisters a virtual machine server.
        Args:
            vmServerNameOrIP: the virtual machine server's name or IP address
            halt: if True, the virtual machine server will be shut down immediately. If false,
                it will shut down when all its active virtual machines have finished.
        Returns:
            A command ID.
            @attention: DO NOT rely on the command ID's internal representation: it can change without prior notice.
        """
        (commandType, commandArgs) = CommandsHandler.createVMServerUnregistrationOrShutdownCommand(True, vmServerNameOrIP, halt)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def shutdownVMServer(self, vmServerNameOrIP, halt):
        """
        Shutds down a virtual machine server
         Args:
            vmServerNameOrIP: the virtual machine server's name or IP address
            halt: if True, the virtual machine server will be shut down immediately. If false,
                it will shut down when all its active virtual machines have finished.
        Returns:
            A command ID.
            @attention: DO NOT rely on the command ID's internal representation: it can change without prior notice.
        """
        (commandType, commandArgs) = CommandsHandler.createVMServerUnregistrationOrShutdownCommand(False, vmServerNameOrIP, halt)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def bootUpVMServer(self, vmServerNameOrIP):
        """
        Pairs a virtual machine server to the system.
        Args:
            vmServerNameOrIP: the virtual machine server's name or IP address
        Returns:
            A command ID.
            @attention: DO NOT rely on the command ID's internal representation: it can change without prior notice.
        """
        (commandType, commandArgs) = CommandsHandler.createVMServerBootCommand(vmServerNameOrIP)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def bootUpVM(self, vmID):
        """
        Sends a virtual machine boot up request
        Args:
            vmID: the virtual machine's unique identifier
        Returns:
             A command ID.
            @attention: DO NOT rely on the command ID's internal representation: it can change without prior notice.
        """
        (commandType, commandArgs) = CommandsHandler.createVMBootCommand(vmID, self.__userID)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def halt(self, haltVMServers):
        """
        Halt the whole system.
        Args:
            haltVMServers: if True, the virtual machine server will be shut down immediately. If false,
                it will shut down when all its active virtual machines have finished.
        Returns: 
            Nothing
        """
        (commandType, commandArgs) = CommandsHandler.createHaltCommand(haltVMServers)
        self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def getCommandOutput(self, commandID):
        """
        Returns a command's output.
        Args:
            commandID: the command's ID
        Returns:
            None if the command output is not available. Otherwise, it will return a dictionary
            with it.
            This dictionary will have the keys 
            - ServerNameOrIPAddress and ErrorMessage if the command output is a 
              virtual machine server boot up error.
            - VMServerIP, VMServerPort, VMServerName and ErrorMessage if the command output
              is a virtual machine server registration error.
            - VMID and ErrorMessage if the command output is a virtual machine boot failure.
            - VNCServerIPAddress, VNCServerPort and VNCServerPassword if the command otput
              contains a virtual machine's connection data.
        """
        result = self.__commandsDBConnector.getCommandOutput(commandID)
        if (result != None) :
            (outputType, outputContent) = result
            result = CommandsHandler.deserializeCommandOutput(outputType, outputContent)
        return result
    
    def waitForCommandOutput(self, commandID):
        """
        Returns a command's output
        Args:
            commandID: the command's ID
        Returns: A dictionary containing the command's output.
        This dictionary will have the keys 
            - ServerNameOrIPAddress and ErrorMessage if the command output is a 
              virtual machine server boot up error.
            - VMServerIP, VMServerPort, VMServerName and ErrorMessage if the command output
              is a virtual machine server registration error.
            - VMID and ErrorMessage if the command output is a virtual machine boot failure.
            - VNCServerIPAddress, VNCServerPort and VNCServerPassword if the command otput
              contains a virtual machine's connection data.
        @attention: This method will only return when the command output is available. If you prefer
        a non-blocking behavior, use getCommandOutput() instead.
        """
        result = None
        while (result == None) :
            result = self.__commandsDBConnector.getCommandOutput(commandID)
            if (result == None) :
                sleep(0.1)
        return CommandsHandler.deserializeCommandOutput(result[0], result[1])
    
if __name__ == "__main__":
    connector = ClusterServerConnector(1)
    connector.connectToDatabases("SystemStatusDB", "CommandsDB", "website", "CygnusCloud")
    sleep(3)
    print connector.getVMServersData()
    connector.unregisterVMServer("Server1", True)
    sleep(5)
    print connector.getVMServersData()
    sleep(10)
    connector.registerVMServer("127.0.0.1", 15800, "DummyVMServer")
    sleep(5)
    print connector.getVMServersData()
    connector.halt(True)
    connector.dispose()
    