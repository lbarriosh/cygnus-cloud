# -*- coding: utf8 -*-
'''
Created on Apr 21, 2013

@author: luis
'''

from ccutils.enums import enum

PACKET_T = enum("HALT", "ADD_IMAGE", "ADDED_IMAGE_ID", "RETR_REQUEST", "RETR_REQUEST_RECVD", "RETR_REQUEST_ERROR", "RETR_START", "RETR_ERROR",
                "STOR_REQUEST", "STOR_REQUEST_RECVD", "STOR_REQUEST_ERROR", "STOR_START", "STOR_ERROR",
                "DELETE_REQUEST", "DELETE_REQUEST_RECVD", "DELETE_REQUEST_ERROR")

class ImageRepositoryPacketHandler(object):
    def __init__(self, packetCreator):
        self.__packetCreator = packetCreator
            
    def createHaltPacket(self):
        p = self.__packetCreator.createPacket(1)
        p.writeInt(PACKET_T.HALT)
        return p
    
    def createRetrieveRequestPacket(self, imageID, modify):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.RETR_REQUEST)
        p.writeInt(imageID)
        p.writeBool(modify)
        return p
    
    def createStoreRequestPacket(self, imageID):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.STOR_REQUEST)
        p.writeInt(imageID)
        return p
    
    def createImageRequestReceivedPacket(self, packet_t):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(packet_t)
        return p
    
    def createTransferEnabledPacket(self, packet_t, imageID, FTPServerPort, username, password, serverDirectory, fileName):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(packet_t)
        p.writeInt(imageID)
        p.writeInt(FTPServerPort)
        p.writeString(username)
        p.writeString(password)
        p.writeString(serverDirectory)
        p.writeString(fileName)
        return p
    
    def createErrorPacket(self, packet_t, errorMessage):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(packet_t)
        p.writeString(errorMessage)
        return p
    
    def createAddImagePacket(self):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.ADD_IMAGE)
        return p
    
    def createAddedImagePacket(self, imageID):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.ADDED_IMAGE_ID)
        p.writeInt(imageID)
        return p
    
    def createDeleteRequestPacket(self, imageID):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.DELETE_REQUEST)
        p.writeInt(imageID)
        return p
    
    def readPacket(self, p):
        data = dict()
        packet_type = p.readInt()
        data['packet_type'] = packet_type
        (data['clientIP'], data['clientPort']) = p.getSenderData()
        if (packet_type == PACKET_T.ADDED_IMAGE_ID):
            data['addedImageID'] = p.readInt()
        elif (packet_type == PACKET_T.RETR_REQUEST) :
            data['imageID'] = p.readInt()
            data['modify'] = p.readBool()
        elif (packet_type == PACKET_T.STOR_REQUEST) :
            data['imageID'] = p.readInt()
        elif (packet_type == PACKET_T.RETR_REQUEST_ERROR or packet_type == PACKET_T.STOR_REQUEST_ERROR or 
              packet_type == PACKET_T.DELETE_REQUEST_ERROR or packet_type == PACKET_T.RETR_ERROR or 
              packet_type == PACKET_T.STOR_ERROR) :
            data['errorMessage'] = p.readString()
        elif (packet_type == PACKET_T.RETR_START or packet_type == PACKET_T.STOR_START) :
            data['imageID'] = p.readInt()
            data['FTPServerPort'] = p.readInt()
            data['username'] = p.readString()
            data['password'] = p.readString()
            data['serverDirectory'] = p.readString()
            data['fileName'] = p.readString()
        elif (packet_type == PACKET_T.DELETE_REQUEST):
            data['imageID'] = p.readInt()
        return data 
