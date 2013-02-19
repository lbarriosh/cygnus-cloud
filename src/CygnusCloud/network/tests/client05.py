# -*- coding: utf8 -*-
'''
A simple client test
@author: Luis Barrios Hernández
@version: 1.0
'''

from network.manager.networkManager import NetworkManager
from network.tests.dummyCallback import DummyCallback
from time import sleep

if __name__ == "__main__" :
    networkManager = NetworkManager("/home/luis/Certificates")
    networkManager.startNetworkService()
    networkManager.connectTo('127.0.0.1', 8080, 20, DummyCallback(), True, True)
    sleep(2)
    p = networkManager.createPacket(0)
    p.writeString("Greetings from a client")    
    networkManager.sendPacket('127.0.0.1', 8080, p)
    sleep(60)
    p = networkManager.createPacket(0)
    p.writeString("Greetings from a client 1")    
    networkManager.sendPacket('127.0.0.1', 8080, p)
    sleep(200)
    networkManager.stopNetworkService()
