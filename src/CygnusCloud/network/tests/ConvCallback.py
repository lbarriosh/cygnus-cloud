# -*- coding: utf8 -*-
from network.manager.networkManager import NetworkCallback

class ConvCallback(NetworkCallback):
    def __init__(self,listP):
        self.listP = listP
    def processPacket(self, packet):
        self.listP.append(packet.readString())
