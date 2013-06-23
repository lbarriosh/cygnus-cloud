# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: fileTransferThread.py    
    Version: 5.0
    Description: file transfer thread definitions
    
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

from ccutils.threads.basicThread import BasicThread
from imageRepository.packetHandling.packetHandler import ImageRepositoryPacketHandler
from virtualMachineServer.packetHandling.packet_t import VM_SERVER_PACKET_T
from time import sleep
from virtualMachineServer.database.transfer_t import TRANSFER_T
from errors.codes import ERROR_DESC_T
from ccutils.processes.childProcessManager import ChildProcessManager
from os import path
from virtualMachineServer.threads.fileTransferCallback import FileTransferCallback

class FileTransferThread(BasicThread):
    """
    This thread class is associated with the transfer thread
    """
    def __init__(self, networkManager, serverListeningPort, packetHandler,
                 transferDirectory, ftpTimeout, maxTransferAttempts, dbConnector, useSSL, max_cancel_timeout = 60):
        """
        Initializes the transfer thread's state
        Args:
            networkManager: the network manager to use
            serverListeningPort: the control connection's port
            packetHandler: the virtual machine server packet handler to use
            transferDirectory: the directory where the .zip files will be stored
            ftpTimeout: the FTP timeout (in seconds)
            maxTransferAttempts: the maximum number of times that a transfer will be restarted after a failure.
            dbConnector: a database connector
            useSSL: indicates wheter SSL encryption must be used when establishing the connection with the image repository or not
            max_cancel_timeout: unlock transfers timeout (in seconds)
        """
        BasicThread.__init__(self, "File transfer thread")
        self.__networkManager = networkManager
        self.__serverListeningPort = serverListeningPort
        self.__transferDirectory = transferDirectory
        self.__repositoryPacketHandler = ImageRepositoryPacketHandler(self.__networkManager)
        self.__vmServerPacketHandler = packetHandler
        self.__ftpTimeout = ftpTimeout
        self.__maxTransferAttempts = maxTransferAttempts
        self.__dbConnector = dbConnector
        self.__max_cancel_timeout = max_cancel_timeout
        self.__useSSL = useSSL
        
    def run(self):
        while not self.finish() :
            data = self.__dbConnector.peekFromTransferQueue()
            if data == None :
                sleep(0.5)
            else :
                self.__processElement(data)        
                self.__dbConnector.removeFirstElementFromTransferQueue()
        
    def __processElement(self, data):
        """
        Performs a transfer request
        Args:
            data: a dictionary containing the request's data
        Returns:
            Nothing
        """
        attempts = 0
        while attempts < self.__maxTransferAttempts :
            try :          
                # Prepare for the new transfer
                
                if (data["Transfer_Type"] == TRANSFER_T.CREATE_IMAGE or data["Transfer_Type"] == TRANSFER_T.EDIT_IMAGE) :
                    p = self.__repositoryPacketHandler.createRetrieveRequestPacket(data["SourceImageID"], data["Transfer_Type"] == TRANSFER_T.EDIT_IMAGE)
                    sourceFilePath = None
                elif (data["Transfer_Type"] == TRANSFER_T.DEPLOY_IMAGE):
                    p = self.__repositoryPacketHandler.createRetrieveRequestPacket(data["SourceImageID"], False)
                    sourceFilePath = None
                elif (data["Transfer_Type"] == TRANSFER_T.STORE_IMAGE):
                    p = self.__repositoryPacketHandler.createStoreRequestPacket(int(data["TargetImageID"]))
                    sourceFilePath = data["SourceFilePath"]
                else :
                    p = self.__repositoryPacketHandler.createCancelEditionPacket(data["ImageID"])
                    
                # Establish the connection with the image repository
                callback = FileTransferCallback(self.__repositoryPacketHandler, self.__transferDirectory, data["RepositoryIP"], self.__ftpTimeout,
                                                 sourceFilePath)
                callback.prepareForNewTransfer()
                self.__networkManager.connectTo(data["RepositoryIP"], data["RepositoryPort"], 
                                                self.__ftpTimeout, callback, self.__useSSL)
                while not self.__networkManager.isConnectionReady(data["RepositoryIP"], data["RepositoryPort"]) :
                    sleep(0.1)
                    
                # Send the transfer request packet
                    
                self.__networkManager.sendPacket(data["RepositoryIP"], data["RepositoryPort"], p)
                
                
                if (data["Transfer_Type"] != TRANSFER_T.CANCEL_EDITION) :
                    # Wait until the transfer finishes
                    while not callback.isTransferCompleted() :
                        sleep(0.1)
                    timeout = False
                else :
                    elapsed_time = 0
                    while not callback.isTransferCompleted() and elapsed_time < self.__max_cancel_timeout:
                        sleep(0.1)
                        elapsed_time += 0.1
                    timeout = elapsed_time >= self.__max_cancel_timeout
                    
                if (callback.getErrorDescription() != None or timeout) :
                    if callback.getImageNotFound() :
                        attempts = self.__maxTransferAttempts
                    else:
                        attempts += 1
                    if (attempts == self.__maxTransferAttempts):
                        if (data["Transfer_Type"] != TRANSFER_T.CANCEL_EDITION):                        
                            # Error => abort the transfer and warn the user
                            p = self.__vmServerPacketHandler.createErrorPacket(VM_SERVER_PACKET_T.IMAGE_EDITION_ERROR, 
                                                                               callback.getErrorDescription(), 
                                                                               data["CommandID"])
                        else :
                            p = self.__vmServerPacketHandler.createInternalErrorPacket(data["CommandID"])
                            
                        self.__networkManager.sendPacket('', self.__serverListeningPort, p)      
                    else:
                        sleep(4**attempts)              
                else :       
                    # The transfer has finished => do something with the .zip file
                    
                    if (data["Transfer_Type"] == TRANSFER_T.CREATE_IMAGE):
                        # Image creation => ask for a new image ID and add a request to the compression queue
                        callback.prepareForNewTransfer()
                        self.__networkManager.sendPacket(data["RepositoryIP"], data["RepositoryPort"], self.__repositoryPacketHandler.createAddImagePacket())
                        while not callback.isTransferCompleted() :
                            sleep(0.1)
                        data["TargetImageID"] = callback.getDomainImageID()
                        self.__dbConnector.addToCompressionQueue(data)
                    elif (data["Transfer_Type"] == TRANSFER_T.EDIT_IMAGE or data["Transfer_Type"] == TRANSFER_T.DEPLOY_IMAGE):
                        # Add a request to the compression queue
                        data["TargetImageID"] = data["SourceImageID"]
                        self.__dbConnector.addToCompressionQueue(data)
                    elif (data["Transfer_Type"] == TRANSFER_T.STORE_IMAGE) :
                        # The image was successfully uploaded => delete the .zip file and send the confirmation packet
                        ChildProcessManager.runCommandInForeground("rm " + path.join(self.__transferDirectory, data["SourceFilePath"]), Exception)
                        p = self.__vmServerPacketHandler.createImageEditedPacket(data["TargetImageID"], data["CommandID"])
                        self.__networkManager.sendPacket('', self.__serverListeningPort, p)
                    
                # Disconnect from the image repository
                self.__networkManager.closeConnection(data["RepositoryIP"], data["RepositoryPort"])
                attempts = self.__maxTransferAttempts
    
            except Exception:
                # Something went wrong => increment the attempts counter and, if necessary, abort the transfer and warn the user
                attempts += 1
                if (attempts == self.__maxTransferAttempts) :
                    errorCode = ERROR_DESC_T.VMSRVR_IR_CONNECTION_ERROR
                    try :
                        self.__networkManager.closeConnection(data["RepositoryIP"], data["RepositoryPort"])
                    except Exception:
                        pass
                    p = self.__vmServerPacketHandler.createErrorPacket(VM_SERVER_PACKET_T.IMAGE_EDITION_ERROR, 
                                                                        errorCode, 
                                                                           data["CommandID"])
                    self.__networkManager.sendPacket('', self.__serverListeningPort, p)
                else:
                    sleep(4**attempts)