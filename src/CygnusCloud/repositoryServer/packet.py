#coding=utf-8
from ccutils.enums import enum

REPOSITORY_PACKET_T = enum("IMAGE_SEND", "ACCEPTED_PETITION", "UPLOAD_SLOT",
                           "DOWNLOAD_SLOT")

class RepositoryPacketHandler(object):
    
    def __init__(self, networkManager):
        self.__packetCreator = networkManager
    
    def createImageSendPacket(self, sendID):
        packet = self.__packetCreator.createPacket(5)
        packet.writeInt(REPOSITORY_PACKET_T.IMAGE_SEND)
        packet.writeInt(sendID)
        return packet
    
    def createAcceptedPetition(self, petitionID):
        packet = self.__packetCreator.createPacket(5)
        packet.writeInt(REPOSITORY_PACKET_T.ACCEPTED_PETITION)
        packet.writeInt(petitionID)
        return packet
    
    def createUploadSlotPacket(self, requestID):
        packet = self.__packetCreator.createPacket(5)
        packet.writeInt(REPOSITORY_PACKET_T.UPLOAD_SLOT)
        packet.writeInt(requestID)
        return packet
    def createDownloadSlotPacket(self, requestID):
        packet = self.__packetCreator.createPacket(5)
        packet.writeInt(REPOSITORY_PACKET_T.DOWNLOAD_SLOT)
        packet.writeInt(requestID)
        return packet
    
    def readPacket(self, p):
        data = dict()
        packet_type = p.readInt()
        data["packet_type"] = packet_type
        if (packet_type == REPOSITORY_PACKET_T.IMAGE_SEND):
            data["SendID"] = p.readInt()
        elif (packet_type == REPOSITORY_PACKET_T.ACCEPTED_PETITION):
            data["petitionID"] = p.readInt()
        elif (packet_type == REPOSITORY_PACKET_T.UPLOAD_SLOT or
              packet_type == REPOSITORY_PACKET_T.DOWNLOAD_SLOT):
            data["requestID"] = p.readInt()
        return data