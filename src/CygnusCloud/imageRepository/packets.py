'''
Created on Apr 21, 2013

@author: luis
'''

from ccutils.enums import enum

PACKET_T = enum("STORE_REQUEST", "READY_TO_STORE", "STORE_REQUEST_RECEIVED", "")

class RepositoryPacketHandler(object):
    def __init__(self, packetCreator):
        self.__packetCreator = packetCreator
        
    def createStoreRequestPacket(self, client_ip, client_port):
        p = self.__packetCreator.createPacket(5)
        p.writeInt(PACKET_T.STORE_REQUEST)
        p.writeString(client_ip)
        p.writeInt(client_port)
        return p
    
    def readPacket(self, p):
        data = dict()
        packet_type = p.readInt()
        data['packet_type'] = packet_type
        if (packet_type == PACKET_T.STORE_REQUEST):
            data['client_ip'] = p.readString()
            data['client_port'] = p.readInt()
        return data
    
    def createReplyPacket(self, packet_T):
        
