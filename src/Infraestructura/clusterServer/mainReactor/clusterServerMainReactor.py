# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: clusterServerMainReactor.py    
    Version: 5.0
    Description: cluster server main reactor definitions
    
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

from time import sleep
from errors.codes import ERROR_DESC_T
from ccutils.databases.configuration import DBConfigurator
from network.manager.networkManager import NetworkManager
from clusterServer.callbacks.clusterEndpointCallback import ClusterEndpointCallback
from clusterServer.callbacks.imageRepositoryCallback import ImageRepositoryCallback
from clusterServer.callbacks.vmServerCallback import VMServerCallback
from clusterServer.reactors.endpointPacketReactor import EndpointPacketReactor
from clusterServer.reactors.vmServerPacketReactor import VMServerPacketReactor
from clusterServer.reactors.imageRepositoryReactor import ImageRepositoryPacketReactor
from clusterServer.reactors.networkEventsReactor import NetworkEventsReactor
from clusterServer.packetHandling.packetHandler import ClusterServerPacketHandler
from clusterServer.packetHandling.packet_t import  CLUSTER_SERVER_PACKET_T
from virtualMachineServer.packetHandling.packetHandler import VMServerPacketHandler
from imageRepository.packetHandling.packetHandler import ImageRepositoryPacketHandler
from clusterServer.threads.clusterStatusMonitoringThread import ClusterStatusMonitoringThread
from clusterServer.database.clusterServerDB import ClusterServerDatabaseConnector
from clusterServer.database.server_state_t import SERVER_STATE_T

class ClusterServerMainReactor(object):
    '''
    This class is associated with the cluster server main reactor.
    '''
    def __init__(self, loadBalancerSettings, averageCompressionRatio, timeout):
        """
        Initializes the reactor's state
        Args:
            loadBalancerSettings: a list containing the load balancing algorithm settings
            averageCompressionRation: the compression algorithm's average compression ratio
            timeout: the virtual machine boot commands timeout
        """        
        self.__exit = False
        self.__loadBalancerSettings = loadBalancerSettings
        self.__averageCompressionRatio = averageCompressionRatio
        self.__timeout = timeout
        self.__statusMonitoringThread = None
        
    def connectToDatabase(self, mysqlRootsPassword, dbName, dbUser, dbPassword, scriptPath):
        """
        Establishes a connection with the cluster server database
        Args:
            mysqlRootsPassword: the MySQL root user's password
            dbName: a database name
            dbUser: a MySQL user name
            dbPassword: the user's password
            scriptPath: the schema definition script
        Returns:
            Nothing
        """
        configurator = DBConfigurator(mysqlRootsPassword)
        configurator.runSQLScript(dbName, scriptPath, "root", mysqlRootsPassword) 
        configurator.addUser(dbUser, dbPassword, dbName, True)
        self.__dbConnector = ClusterServerDatabaseConnector(dbUser, dbPassword, dbName)
        self.__dbConnector.initializeVMServersStatus()
        
    def startListenning(self, useSSL, certificatePath, listenningPort, repositoryIP, repositoryPort, vmServerStatusUpdateInterval):
        """
        Creates the control connection
        Args:
            useSSL: indicates if SSL encryption must be used in the control connection or not
            certificatePath: the directory where the server.crt and server.key files are
            listenningPort: the control connection's port
            repositoryIP: the image repository IP address
            repositoryPort: the image repository's port
            vmServerStatusUpdateInterval: the virtual machine server status database interval
        Returns:
            Nothing
        """            
        
        self.__networkManager = NetworkManager(certificatePath)        
        self.__networkManager.startNetworkService()    
        self.__listenningPort = listenningPort
        self.__packetHandler = ClusterServerPacketHandler(self.__networkManager)    
        self.__useSSL = useSSL
        imageRepositoryPacketHandler = ImageRepositoryPacketHandler(self.__networkManager)
        vmServerPacketHandler = VMServerPacketHandler(self.__networkManager)        
        networkEventsReactor = NetworkEventsReactor(self.__dbConnector, repositoryIP, repositoryPort)
        
        
        imageRepositoryPacketReactor = ImageRepositoryPacketReactor(self.__dbConnector, self.__networkManager,
                                                                    listenningPort, repositoryIP, repositoryPort,
                                                                    self.__packetHandler, vmServerPacketHandler, imageRepositoryPacketHandler)
        try :
            imageRepositoryCallback = ImageRepositoryCallback(imageRepositoryPacketReactor, networkEventsReactor)
            self.__networkManager.connectTo(repositoryIP, repositoryPort, 10, imageRepositoryCallback, self.__useSSL, True)
            self.__dbConnector.addImageRepository(repositoryIP, repositoryPort, SERVER_STATE_T.READY) 
        except Exception as e:
            print "Can't connect to the image repository: " + e.message
            self.__exit = True
            return        
        
        vmServerPacketReactor = VMServerPacketReactor(self.__dbConnector, self.__networkManager, listenningPort,
                                                      vmServerPacketHandler, self.__packetHandler)
        
        self.__endpointPacketReactor = EndpointPacketReactor(self.__dbConnector, self.__networkManager, 
                                                             vmServerPacketHandler, self.__packetHandler,
                                                             imageRepositoryPacketHandler,
                                                             VMServerCallback(vmServerPacketReactor, networkEventsReactor),
                                                             listenningPort, repositoryIP, repositoryPort, self.__loadBalancerSettings,
                                                             self.__averageCompressionRatio, self.__useSSL) 
        clusterEndpointCallback = ClusterEndpointCallback(self.__endpointPacketReactor)
        self.__networkManager.listenIn(listenningPort, clusterEndpointCallback, self.__useSSL)
       
        self.__statusMonitoringThread = ClusterStatusMonitoringThread(vmServerStatusUpdateInterval,
                                                                      self.__dbConnector, self.__networkManager,
                                                                      repositoryIP, repositoryPort,
                                                                      vmServerPacketHandler, imageRepositoryPacketHandler)
        self.__statusMonitoringThread.start()           
    
    def monitorVMBootCommands(self):
        """
        Deletes the timed out virtual machine boot commands
        Args:
            None
        Returns:
            Nothing
        """
        
        while not self.__exit and not self.__endpointPacketReactor.hasFinished():
            data = self.__dbConnector.getOldVMBootCommandID(self.__timeout)
            if (data == None) :               
                sleep(1) 
            else :                
                self.__dbConnector.deleteActiveVMLocation(data[0])
                p = self.__packetHandler.createErrorPacket(CLUSTER_SERVER_PACKET_T.VM_BOOT_FAILURE, ERROR_DESC_T.CLSRVR_VM_BOOT_TIMEOUT, data[0])
                self.__networkManager.sendPacket('', self.__listenningPort, p)
    
    def closeNetworkConnections(self):
        """
        Closes the control connection
        Args:
            None
        Returns:
            Nothing
        """
        if (self.__statusMonitoringThread != None) :
            self.__statusMonitoringThread.stop()
        self.__networkManager.stopNetworkService()    