# -*- coding: utf8 -*-
'''
Created on Apr 21, 2013

@author: luis
'''

from ccutils.enums import enum

PACKET_T = enum("STORE_REQUEST", "READY_TO_STORE", "STORE_REQUEST_RECEIVED", "HALT", "ADD_IMAGE", "ADDED_IMAGE_ID")

class ImageRepositoryPacketHandler(object):
    def __init__(self, packetCreator):
        self.__packetCreator = packetCreator
            
    def createHaltPacket(self):
        p = self.__packetCreator.createPacket(1)
        p.writeInt(PACKET_T.HALT)
        return p
    
    def createStoreRequestPacket(self):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.STORE_REQUEST)
        return p
    
    def createReplyPacket(self, packet_T):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(packet_T)
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
        return data 
