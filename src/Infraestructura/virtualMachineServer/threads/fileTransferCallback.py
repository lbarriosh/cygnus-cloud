# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: fileTransferCallback.py    
    Version: 4.0
    Description: image repository network callback
    
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

from network.manager.networkManager import NetworkCallback
from ftp.ftpClient import FTPClient
from errors.codes import ERROR_DESC_T
from imageRepository.packetHandling.packet_t import PACKET_T as IR_PACKET_T

class FileTransferCallback(NetworkCallback):
    """
    Image repository network callback
    """    
    def __init__(self, packetHandler, transferDirectory, imageRepositoryIP, ftpTimeout, sourceFilePath=None):
        """
        Initializes the callback's state
        Args:
            packetHandler: the image repository packet handler to use
            transferDirectory: the directory where the .zip files will be stored
            imageRepositoryIP: the image repository's IPv4 address
            ftpTimeout: the FTP timeout (in seconds)
            sourceFilePath: the file to upload's path. It will only be used on FTP STOR transfers.
        """
        self.__repositoryPacketHandler = packetHandler
        self.__operation_completed = False
        self.__errorDescription = None
        self.__transferDirectory = transferDirectory
        self.__ftpServerIP = imageRepositoryIP
        self.__ftpTimeout = ftpTimeout
        self.__imageID = None
        self.__sourceFilePath = sourceFilePath
        
    def isTransferCompleted(self):
        """
        Checks if the active transfer has finished or not
        Args:
            None
        Returns:
            True if the active transfer has finished, and false otherwise
        """
        return self.__operation_completed
    
    def getErrorDescription(self):
        """
        Returns the error description code sent by the image repository
        Args:
            None
        Returns: the error description code sent by the image repository
        """
        return self.__errorDescription
    
    def getDomainImageID(self):
        """
        Returns the allocated image ID
        Args:
            None
        Returns:
            The allocated image ID
        """
        return self.__imageID
    
    def prepareForNewTransfer(self):
        """
        Prepares the callback for a new transfer
        Args:
            None
        Returns:
            Nothing
        """
        self.__errorDescription = None
        self.__operation_completed = False
        self.__image_not_found = False
        
    def getImageNotFound(self):
        """
        Checks if the image was not found on the image repository or not.
        Args:
            None
        Returns:
            True if the image was not found on the image repository, and False otherwise.
        """
        return self.__image_not_found
    
    def processPacket(self, packet):
        """
        Processes a packet sent from the image repository
        Args:
            packet: the incoming packet to process
        Returns:
            Nothing
        """
        data = self.__repositoryPacketHandler.readPacket(packet)
        if (data["packet_type"] == IR_PACKET_T.RETR_REQUEST_RECVD or
            data["packet_type"] == IR_PACKET_T.STOR_REQUEST_RECVD) :
            return
        elif (data["packet_type"] == IR_PACKET_T.RETR_REQUEST_ERROR or data["packet_type"] == IR_PACKET_T.RETR_ERROR or
              data["packet_type"] == IR_PACKET_T.STOR_REQUEST_ERROR or data["packet_type"] == IR_PACKET_T.STOR_ERROR) :
            self.__errorDescription = data["errorDescription"]
            self.__image_not_found = True
        elif (data["packet_type"] == IR_PACKET_T.RETR_START) :
            try :
                ftpClient = FTPClient()
                ftpClient.connect(self.__ftpServerIP, data['FTPServerPort'], self.__ftpTimeout, data['username'], data['password'])
                ftpClient.retrieveFile(data['fileName'], self.__transferDirectory, data['serverDirectory']) 
                ftpClient.disconnect()
            except Exception:
                self.__errorDescription = ERROR_DESC_T.VMSRVR_FTP_RETR_TRANSFER_ERROR
        elif (data["packet_type"] == IR_PACKET_T.STOR_START) :
            try :
                ftpClient = FTPClient()
                ftpClient.connect(self.__ftpServerIP, data['FTPServerPort'], self.__ftpTimeout, data['username'], data['password'])
                ftpClient.storeFile(self.__sourceFilePath, self.__transferDirectory, data['serverDirectory'])
                ftpClient.disconnect()
            except Exception:
                self.__errorDescription = ERROR_DESC_T.VMSRVR_FTP_RETR_TRANSFER_ERROR
        elif (data["packet_type"] == IR_PACKET_T.ADDED_IMAGE_ID):
            self.__imageID = data["addedImageID"]                  
        self.__operation_completed = True   