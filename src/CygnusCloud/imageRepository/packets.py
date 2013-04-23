# -*- coding: utf8 -*-
'''
Created on Apr 21, 2013

@author: luis
'''

from ccutils.enums import enum

PACKET_T = enum("HALT", "ADD_IMAGE", "ADDED_IMAGE_ID", "RETR_REQUEST", "RETR_REQUEST_RECVD", "RETR_REQUEST_ERROR")

class ImageRepositoryPacketHandler(object):
    def __init__(self, packetCreator):
        self.__packetCreator = packetCreator
            
    def createHaltPacket(self):
        p = self.__packetCreator.createPacket(1)
        p.writeInt(PACKET_T.HALT)
        return p
    
    def createImageRequestPacket(self, packet_t, imageID):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(packet_t)
        p.writeInt(imageID)
        return p
    
    def createImageRequestReceivedPacket(self, packet_t):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(packet_t)
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
    
    def readPacket(self, p):
        data = dict()
        packet_type = p.readInt()
        data['packet_type'] = packet_type
        (data['clientIP'], data['clientPort']) = p.getSenderData()
        if (packet_type == PACKET_T.ADDED_IMAGE_ID):
            data['addedImageID'] = p.readInt()
        elif (packet_type == PACKET_T.RETR_REQUEST) :
            data['imageID'] = p.readInt()
        elif (packet_type == PACKET_T.RETR_REQUEST_ERROR) :
            data['errorMessage'] = p.readString()
        return data 
