# -*- coding: utf8 -*-
'''
A simple client test
@author: Luis Barrios Hernández
@version: 1.0
'''

from network.manager import NetworkManager
from network.tests.dummyCallback import DummyCallback
from time import sleep

if __name__ == "__main__" :
    networkManager = NetworkManager()
    networkManager.startNetworkService()
    networkManager.connectTo('192.168.0.5', 8080, 20, DummyCallback())
    p = networkManager.createPacket(0)
    p.writeString("Greetings from a client")
    for i in range(100) :
        networkManager.sendPacket(8080, p)
    sleep(100000)
    networkManager.stopNetworkService()
