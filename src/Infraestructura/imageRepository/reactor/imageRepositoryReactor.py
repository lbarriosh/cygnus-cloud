# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: imageRepositoryPacketReactor.py    
    Version: 3.0
    Description: image repository packet reactor
    
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

from network.manager.networkManager import NetworkManager
from imageRepository.database.imageRepositoryDB import ImageRepositoryDBConnector
from ftp.configurableFTPServer import ConfigurableFTPServer
from ccutils.dataStructures.multithreadingList import GenericThreadSafeList
from ccutils.dataStructures.multithreadingCounter import MultithreadingCounter
from time import sleep
from ccutils.processes.childProcessManager import ChildProcessManager
from errors.codes import ERROR_DESC_T
from imageRepository.callbacks.ftpServerCallback import FTPServerCallback
from imageRepository.callbacks.packetsCallback import CommandsCallback
from imageRepository.packetHandling.packet_t import PACKET_T
from imageRepository.packetHandling.packetHandler import ImageRepositoryPacketHandler
from os import path, mkdir

class ImageRepositoryReactor(object):
    """
    Image repository packet reactor
    """    
    
    def __init__(self, workingDirectory):
        """
        Initializes the reactor's state
        Args:
            workingDirectory: the FTP server's root directory
        """
        self.__workingDirectory = workingDirectory        
        self.__slotCounter = MultithreadingCounter()
        self.__retrieveQueue = GenericThreadSafeList()
        self.__storeQueue = GenericThreadSafeList() 
        self.__finish = False   
        self.__networkManager = None
        self.__ftpServer = None    
    
    def connectToDatabase(self, repositoryDBName, repositoryDBUser, repositoryDBPassword):
        """
        Establishes the connection with the image repository's database.
        Args:
            repositoryDBName: a database name
            repositoryDBUser: an user name
            repositoryDBPassword: a password
        Returns:
            Nothing
        """
        self.__dbConnector = ImageRepositoryDBConnector(repositoryDBUser, repositoryDBPassword, repositoryDBName)
    
    def startListenning(self, networkInterface, useSSL, certificatesDirectory, commandsListenningPort, ftpListenningPort, maxConnections,
                        maxConnectionsPerIP, uploadBandwidthRatio, downloadBandwidthRatio, ftpUsername, ftpPasswordLength): 
        """
        Boots up the FTP server and creates the control connection.
        Args:
            networkInterface: the network interface that will be used by the FTP server
            certificatesDirectory: the directory where the files server.crt and server.key are
            commandsListenningPort: the control connection's port
            ftpListenningPort: the FTP server listenning port
            maxConnections: maximum FTP connections
            maxConnectionsPerIP: maximum FTP connections per IP address
            uploadBandwidthRatio: maximum download bandwidth fraction
            downloadBandwidthRatio: maximum upload bandwidth fraction
            ftpUsername: the FTP user that the virtual machine servers will use
            ftpPasswordLength: the random FTP password length
        Returns:
            Nothing
        @attention: The FTP password will be randomly generated at every boot.
        """
        try :
            self.__maxConnections = maxConnections      
            self.__commandsListenningPort = commandsListenningPort
            self.__FTPListenningPort = ftpListenningPort
            self.__networkManager = NetworkManager(certificatesDirectory)
            self.__repositoryPacketHandler = ImageRepositoryPacketHandler(self.__networkManager)        
            
            self.__commandsCallback = CommandsCallback(self.__networkManager, self.__repositoryPacketHandler, commandsListenningPort, self.__dbConnector,
                                                       self.__retrieveQueue, self.__storeQueue, self.__workingDirectory)        
            
            self.__networkManager.startNetworkService()
            self.__networkManager.listenIn(commandsListenningPort, self.__commandsCallback, useSSL)
            
            dataCallback = FTPServerCallback(self.__slotCounter, self.__dbConnector)
            
            self.__ftpUsername = ftpUsername
            self.__ftpPassword = ChildProcessManager.runCommandInForeground("openssl rand -base64 {0}".format(ftpPasswordLength), Exception)        
            
            self.__ftpServer = ConfigurableFTPServer("Image repository FTP Server")
       
            self.__ftpServer.startListenning(networkInterface, ftpListenningPort, maxConnections, maxConnectionsPerIP, 
                                             dataCallback, downloadBandwidthRatio, uploadBandwidthRatio)
            self.__ftpServer.addUser(self.__ftpUsername, self.__ftpPassword, self.__workingDirectory, "eramw")      
        except Exception as e:
            print "Error: " + e.message
            self.__finish = True
        
    def stopListenning(self):
        """
        Stops the FTP server and closes the control connection.
        Args:
            None
        Returns:
            Nothing
        """
        if (self.__ftpServer != None) :
            try :
                self.__ftpServer.stopListenning()
            except Exception :
                pass
        if (self.__networkManager != None) :
            self.__networkManager.stopNetworkService()
    
    def initTransfers(self):
        """
        Initializes the upload and download transfers
        Args:
            None
        Returns:
            Nothing
        """
        store = False
        while not (self.__finish or self.__commandsCallback.haltReceived()):
            if (self.__slotCounter.read() == self.__maxConnections) :
                # No free slots => sleep
                sleep(0.1)
            else :
                # There are slots => enable uploads and downloads in parallel
                self.__slotCounter.decrement()
                
                if (self.__retrieveQueue.isEmpty() and self.__storeQueue.isEmpty()) :
                    sleep(0.1)
                    continue                
                if (not self.__retrieveQueue.isEmpty() and self.__storeQueue.isEmpty()) :
                    queue = self.__retrieveQueue
                    store = False
                elif (self.__retrieveQueue.isEmpty() and not self.__storeQueue.isEmpty()) :
                    queue = self.__storeQueue
                    store = True
                else :
                    if (store) :
                        queue = self.__retrieveQueue
                        store = False
                    else :
                        queue = self.__storeQueue
                        store = True
                
                                   
                (imageID, clientIP, clientPort) = queue.pop(0)
                    
                imageData = self.__dbConnector.getImageData(imageID)
                if (imageData == None) :
                    if (store) :
                        packet_type = PACKET_T.STOR_ERROR
                    else :
                        packet_type = PACKET_T.RETR_ERROR
                    p = self.__repositoryPacketHandler.createErrorPacket(packet_type, ERROR_DESC_T.IR_IMAGE_DELETED)
                    self.__networkManager.sendPacket('', self.__commandsListenningPort, p, clientIP, clientPort)
                else :
                    compressedFilePath = imageData["compressedFilePath"]    
                    
                    if (not "undefined" in compressedFilePath) :                                
                        serverDirectory = path.relpath(path.dirname(compressedFilePath), self.__workingDirectory)
                        compressedFileName = path.basename(compressedFilePath)
                    else :
                        serverDirectory = str(imageID)
                        compressedFileName = ""
                        serverDirectoryPath = path.join(self.__workingDirectory, serverDirectory)
                        if (path.exists(serverDirectoryPath)) :
                            # The directory exists, and can store shit => clean it up!
                            ChildProcessManager.runCommandInForeground("rm -rf " + serverDirectoryPath, Exception)
                        mkdir(serverDirectoryPath)                        
                    
                    if (store) :
                        packet_type = PACKET_T.STOR_START
                    else :
                        packet_type = PACKET_T.RETR_START
                                    
                    p = self.__repositoryPacketHandler.createTransferEnabledPacket(packet_type, imageID, self.__FTPListenningPort, 
                                    self.__ftpUsername, self.__ftpPassword, serverDirectory, compressedFileName)
                        
                    self.__networkManager.sendPacket('', self.__commandsListenningPort, p, clientIP, clientPort)