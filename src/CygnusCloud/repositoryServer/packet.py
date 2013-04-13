#coding=utf-8
from ccutils.enums import enum

REPOSITORY_PACKET_T = enum("IMAGE_SEND")

class RepositoryPacketHandler(object):
    
    def __init__(self, networkManager):
        self.__packetCreator = networkManager
    
    def createImageSendPacket(self, sendID):
        packet = self.__packetCreator.createPacket(5)
        packet.writeInt(REPOSITORY_PACKET_T.IMAGE_SEND)
        packet.writeInt(sendID)
        return packet
    
    def readPacket(self, p):
        data = dict()
        packet_type = p.readInt()
        data["packet_type"] = packet_type
        if (packet_type == REPOSITORY_PACKET_T.IMAGE_SEND):
            data["SendID"] = p.readInt()

        return data