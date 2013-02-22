# -*- coding: utf8 -*-
'''
Cluster server class definitions.
@author: Luis Barrios Hernández
@version: 2.0
'''
from database.systemStatusDB.systemStatusDBReader import SystemStatusDatabaseReader
from database.commands.commandsDatabaseConnector import CommandsDatabaseConnector
from clusterServer.connector.commandsHandler import CommandsHandler
from time import sleep

class ClusterServerConnector(object):
    
    def __init__(self, userID):
        self.__userID = userID
    
    def connectToDatabases(self, statusDBName, statusDBUser, statusDBPassword, commandsDBName,
                           commandsDBUser, commandsDBPassword):
        self.__statusDBConnector = SystemStatusDatabaseReader(statusDBUser, statusDBPassword, statusDBName)
        self.__statusDBConnector.connect()
        self.__commandsDBConnector = CommandsDatabaseConnector(commandsDBUser, commandsDBPassword, commandsDBName, 1)
        self.__commandsDBConnector.connect()
        
    def dispose(self):
        self.__statusDBConnector.disconnect()
        self.__commandsDBConnector.disconnect()
        
    def getActiveVMsData(self):
        return self.__statusDBConnector.getActiveVMsData()
    
    def getVMDistributionData(self):
        self.__statusDBConnector.getVMDistributionData()
        
    def getVMServersData(self):
        self.__statusDBConnector.getVMServersData()
        
    def registerVMServer(self, vmServerIP, vmServerPort, vmServerName):
        (commandType, commandArgs) = CommandsHandler.createVMServerRegistrationCommand(vmServerIP, vmServerPort, vmServerName)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
        
    def unregisterVMServer(self, vmServerNameOrIP, halt):
        (commandType, commandArgs) = CommandsHandler.createVMServerUnregistrationOrShutdownCommand(True, vmServerNameOrIP, halt)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def shutdownVMServer(self, vmServerNameOrIP, halt):
        (commandType, commandArgs) = CommandsHandler.createVMServerUnregistrationOrShutdownCommand(False, vmServerNameOrIP, halt)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def bootUpVMServer(self, vmServerNameOrIP):
        (commandType, commandArgs) = CommandsHandler.createVMServerBootCommand(vmServerNameOrIP)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def bootUpVM(self, vmID, userID):
        (commandType, commandArgs) = CommandsHandler.createVMBootCommand(vmID, userID)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def halt(self, haltVMServers):
        (commandType, commandArgs) = CommandsHandler.createHaltCommand(haltVMServers)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def getCommandOutput(self, commandID):
        result = self.__commandsDBConnector.getCommandOutput(commandID)
        if (result != None) :
            (outputType, outputContent) = result
            result = CommandsHandler.deserializeCommandOutput(outputType, outputContent)
        return result
    
    def waitForCommandOutput(self, commandID):
        result = None
        while (result == None) :
            result = self.__commandsDBConnector.getCommandOutput(commandID)
            if (result == None) :
                sleep(0.1)
        return CommandsHandler.deserializeCommandOutput(result[0], result[1])