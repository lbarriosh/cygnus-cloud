# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: packetHandler.py    
    Version: 2.0
    Description: image repository packet handler definitions
    
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
from imageRepository.packetHandling.packet_t import PACKET_T

class ImageRepositoryPacketHandler(object):
    """
    Image repository packet handler
    """        
    def __init__(self, networkManager):
        """
        Initializes the handler's state
        Args:
            networkManager: the object that will create the network packets
        """
        self.__packetCreator = networkManager
            
    def createHaltPacket(self):
        """
        Creates a shutdown packet
        Args:
            None
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(1)
        p.writeInt(PACKET_T.HALT)
        return p
    
    def createCancelEditionPacket(self, imageID):
        p = self.__packetCreator.createPacket(2)
        p.writeInt(PACKET_T.CANCEL_EDITION)
        p.writeInt(imageID)
        return p
    
    def createRetrieveRequestPacket(self, imageID, modify):
        """
        Creates a FTP RETR request packet
        Args:
            imageID: an image ID
            modify: This parameter indicates if the image will be modified in a virtual machine server 
                or not.
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.RETR_REQUEST)
        p.writeInt(imageID)
        p.writeBool(modify)
        return p
    
    def createStoreRequestPacket(self, imageID):
        """
        Creates a FTP STOR request packet
        Args:
            imageID: an image ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.STOR_REQUEST)
        p.writeInt(imageID)
        return p
    
    def createImageRequestReceivedPacket(self, packet_t):
        """
        Creates a request received packet
        Args:
            packet_t: a packet type that matches the confirmation to send.
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(packet_t)
        return p
    
    def createTransferEnabledPacket(self, packet_t, imageID, FTPServerPort, username, password, serverDirectory, fileName):
        """
        Creates a transfer enabled notice packet
        Args:
            packet_t: a packet type that matches the transfer that will start (FTP RETR or FTP STOR)
            imageID: an image ID
            FTPServerPort: the FTP server's listenning port
            username: an FTP user name
            password: the FTP user's password
            serverDirectory: the FTP server's directory where the file is located
            fileName: the file to download/upload's name
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(3)
        p.writeInt(packet_t)
        p.writeInt(imageID)
        p.writeInt(FTPServerPort)
        p.writeString(username)
        p.writeString(password)
        p.writeString(serverDirectory)
        p.writeString(fileName)
        return p
    
    def createErrorPacket(self, packet_t, errorDescription):
        """
        Creates an error packet
        Args:
            packet_t: a packet type that matches the error message to send
            errorDescription: an error description code
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(4)
        p.writeInt(packet_t)
        p.writeInt(errorDescription)
        return p
    
    def createImageDeletionErrorPacket(self, imageID, errorDescription):
        """
        Creates an image deletion error packet
        Args:
            imageID: an image ID
            errorDescription: an error description code
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(2
                                              )
        p.writeInt(PACKET_T.DELETE_REQUEST_ERROR)
        p.writeInt(imageID)
        p.writeInt(errorDescription)
        return p
    
    def createDeleteRequestReceivedPacket(self, imageID):
        """
        Creates an image deletion request packet.
        Args:
            imageID: an image ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.DELETE_REQUEST_RECVD)
        p.writeInt(imageID)
        return p
    
    def createAddImagePacket(self):
        """
        Creates an image ID registration packet
        Args:
            None
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.ADD_IMAGE)
        return p
    
    def createAddedImagePacket(self, imageID):
        """
        Creates a registered image ID packet 
        Args:
            imageID: the new image's ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.ADDED_IMAGE_ID)
        p.writeInt(imageID)
        return p
    
    def createDeleteRequestPacket(self, imageID):
        """
        Creates an image deletion request packet
        Args:
            imageID: an image ID
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.DELETE_REQUEST)
        p.writeInt(imageID)
        return p
    
    def createStatusRequestPacket(self):
        """
        Creates a status request packet
        Args:
            None
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.STATUS_REQUEST)
        return p
    
    def createStatusDataPacket(self, freeDiskSpace, totalDiskSpace):
        """
        Creates an image repository status packet
        Args:
            freeDiskSpace: the free disk space in the image repository
            totalDiskSpace: the available disk space in the image repository
        Returns:
            a packet of the specified type built from this method's arguments
        """
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.STATUS_DATA)
        p.writeInt(freeDiskSpace)
        p.writeInt(totalDiskSpace)
        return p
    
    def readPacket(self, p):
        """
        Reads a packet's content
        Args:
            p: the packet to read
        Returns:
            A dictionary with the packet's content. Its keys and values
            vary depending on the read packet's type.
        """
        data = dict()
        packet_type = p.readInt()
        data['packet_type'] = packet_type
        (data['clientIP'], data['clientPort']) = p.getSenderData()
        if (packet_type == PACKET_T.ADDED_IMAGE_ID):
            data['addedImageID'] = p.readInt()
        elif (packet_type == PACKET_T.RETR_REQUEST) :
            data['imageID'] = p.readInt()
            data['modify'] = p.readBool()
        elif (packet_type == PACKET_T.DELETE_REQUEST or packet_type == PACKET_T.DELETE_REQUEST_RECVD or 
              packet_type == PACKET_T.STOR_REQUEST) :
            data['imageID'] = p.readInt()
        elif (packet_type == PACKET_T.RETR_REQUEST_ERROR or packet_type == PACKET_T.STOR_REQUEST_ERROR or 
              packet_type == PACKET_T.RETR_ERROR or packet_type == PACKET_T.STOR_ERROR) :
            data['errorDescription'] = p.readInt()
        elif (packet_type == PACKET_T.DELETE_REQUEST_ERROR) :            
            data['imageID'] = p.readInt()
            data['errorDescription'] = p.readInt()
        elif (packet_type == PACKET_T.RETR_START or packet_type == PACKET_T.STOR_START) :
            data['imageID'] = p.readInt()
            data['FTPServerPort'] = p.readInt()
            data['username'] = p.readString()
            data['password'] = p.readString()
            data['serverDirectory'] = p.readString()
            data['fileName'] = p.readString()
        elif (packet_type == PACKET_T.STATUS_DATA):       
            data["FreeDiskSpace"] = p.readInt()            
            data["TotalDiskSpace"] = p.readInt()     
        elif (packet_type == PACKET_T.CANCEL_EDITION):
            data["ImageID"] = p.readInt()
        return data 
