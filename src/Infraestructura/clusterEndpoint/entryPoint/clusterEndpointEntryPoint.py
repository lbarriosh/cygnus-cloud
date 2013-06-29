# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: clusterEndpointEntryPoint.py    
    Version: 5.0
    Description: cluster endpoint daemon entry point
    
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

from clusterEndpoint.threads.databaseUpdateThread import VMServerMonitoringThread
from clusterEndpoint.threads.commandMonitoringThread import CommandsMonitoringThread
from clusterServer.packetHandling.packetHandler import ClusterServerPacketHandler
from ccutils.databases.configuration import DBConfigurator
from clusterEndpoint.databases.clusterEndpointDB import ClusterEndpointDBConnector
from network.manager.networkManager import NetworkManager
from time import sleep
from clusterEndpoint.databases.commandsDatabaseConnector import CommandsDatabaseConnector
from network.exceptions.networkManager import NetworkManagerException
from clusterEndpoint.commands.commandsHandler import CommandsHandler
from clusterEndpoint.reactors.commandsProcessor import CommandsProcessor
from clusterEndpoint.reactors.packetReactor import ClusterEndpointPacketReactor
from clusterEndpoint.codes.spanishCodesTranslator import SpanishCodesTranslator

class ClusterEndpointEntryPoint(object):  
    """
    These objects create, run and stop the cluster endpoint daemons.
    """    
    def __init__(self):
        """
        Initializes the daemon's state
        Args:
            None
        """
        self.__commandExecutionThread = None
        self.__updateRequestThread = None
        self.__codeTranslator = SpanishCodesTranslator()
        self.__commandsHandler = CommandsHandler(self.__codeTranslator)       
    
    def connectToDatabases(self, mysqlRootsPassword, endpointDBName, commandsDBName, endpointdbSQLFilePath, commandsDBSQLFilePath,
                           websiteUser, websiteUserPassword, endpointUser, endpointUserPassword, minCommandInterval):
        """
        Establishes the connection with the two databases
        Args:
            mysqlRootsPassword: the MySQL root's password
            endpointDBName: the endpoint database's name
            endpointdbSQLFilePath: the endpoint database's schema definition file path
            websiteUser: the web application's username
            websiteUserPassword: the web application's username
            endpointUser: the endpoint daemon user's name
            endpointUserPassword: the endpoint daemon user's password
        """        
        self.__rootsPassword = mysqlRootsPassword
        self.__statusDatabaseName = endpointDBName
        self.__commandsDatabaseName = commandsDBName
        configurator = DBConfigurator(mysqlRootsPassword)
        configurator.runSQLScript(endpointDBName, endpointdbSQLFilePath, "root", mysqlRootsPassword)
        configurator.runSQLScript(commandsDBName, commandsDBSQLFilePath, "root", mysqlRootsPassword)
        
        configurator.addUser(websiteUser, websiteUserPassword, endpointDBName, False)
        configurator.addUser(endpointUser, endpointUserPassword, endpointDBName, True)
        configurator.addUser(websiteUser, websiteUserPassword, commandsDBName, True)
        configurator.addUser(endpointUser, endpointUserPassword, commandsDBName, True)
        
        self.__commandsDBConnector = CommandsDatabaseConnector(endpointUser, endpointUserPassword, 
                                                               commandsDBName, minCommandInterval) 
        self.__endpointDBConnector = ClusterEndpointDBConnector(endpointUser, endpointUserPassword, endpointDBName)
        
    def connectToClusterServer(self, useSSL, certificatePath, clusterServerIP, clusterServerListenningPort, statusDBUpdateInterval,
                               commandTimeout, commandTimeoutCheckInterval):
        """
        Establishes a connection with the cluster server
        Args:
            certificatePath: the directory where the server.crt and server.key files are
            clusterServerIP: the cluster server's IP address
            clusterServerListenningPort: the cluster server commands connection's port
            statusDBUpdateInterval: the database update interval (in seconds)
        Returns:
            Nothing
        """
        self.__networkManager = NetworkManager(certificatePath)
        self.__networkManager.startNetworkService()

        self.__clusterServerIP = clusterServerIP
        self.__clusterServerPort = clusterServerListenningPort
        self.__packetHandler = ClusterServerPacketHandler(self.__networkManager)     
        self.__commandsProcessor = CommandsProcessor(self.__commandsHandler, self.__packetHandler, self.__networkManager, 
                 self.__clusterServerIP, self.__clusterServerPort, self.__commandsDBConnector, self.__endpointDBConnector)
        packetReactor = ClusterEndpointPacketReactor(self.__codeTranslator, self.__commandsHandler, self.__packetHandler, self.__commandsProcessor,
                                                     self.__endpointDBConnector, self.__commandsDBConnector)
        try :
            self.__networkManager.connectTo(clusterServerIP, clusterServerListenningPort, 5, packetReactor, useSSL)
            while (not self.__networkManager.isConnectionReady(clusterServerIP, clusterServerListenningPort)) :
                sleep(0.1)                   
            self.__updateRequestThread = VMServerMonitoringThread(self.__packetHandler, self.__networkManager, self.__commandsProcessor, 
                                                                  self.__clusterServerIP, self.__clusterServerPort, statusDBUpdateInterval)
            self.__updateRequestThread.start()            
            self.__commandExecutionThread = CommandsMonitoringThread(self.__commandsDBConnector, commandTimeout, self.__commandsHandler, commandTimeoutCheckInterval)
            self.__commandExecutionThread.start()
        except NetworkManagerException as e :
            raise Exception(e.message)
        
    def doEmergencyStop(self):
        """
        Stops the endpoint daemon immediately
        Args:
            None
        Returns:
            Nothing
        """
        self.__networkManager.stopNetworkService()
        if (self.__updateRequestThread != None):
            self.__updateRequestThread.stop()
        if (self.__commandExecutionThread != None):
            self.__commandExecutionThread.stop()        
        
    def disconnectFromClusterServer(self):
        """
        Closes the connection with the cluster server
        Args:
            None
        Devuelve:
            Nada
        """
        p = self.__packetHandler.createHaltPacket(self.__commandsProcessor.haltVMServers())
        errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, p)
        NetworkManager.printConnectionWarningIfNecessary(self.__clusterServerIP, self.__clusterServerPort, "Cluster server halt", 
                                                         errorMessage)
        self.__updateRequestThread.stop()
        
        self.__commandExecutionThread.stop()
        
        self.closeNetworkConnections()
        
    def closeNetworkConnections(self):
        """
        Closes the network connections
        Args:
            None
        Returns:
            Nothing
        """
        self.__networkManager.stopNetworkService()
        
    def processCommands(self):
        """
        Processes the users' requests
        Args:
            None
        Returns:
            Nothing
        """
        self.__commandsProcessor.processCommands()