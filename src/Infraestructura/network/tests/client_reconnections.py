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
    port = 8080
    networkManager = NetworkManager("/home/luis/Certificates")
    networkManager.startNetworkService()
    networkManager.connectTo('127.0.0.1', port, 5, DummyCallback(), True, True)
    sleep(1)
    p = networkManager.createPacket(0)
    p.writeString("Greetings from a client")    
    networkManager.sendPacket('127.0.0.1', port, p)
    networkManager.closeConnection('127.0.0.1', port)
    sleep(5)
    networkManager.connectTo('127.0.0.1', port, 20, DummyCallback(), True, True)
    sleep(1)
    p = networkManager.createPacket(0)
    p.writeString("Greetings from a client 1")    
    networkManager.sendPacket('127.0.0.1', port, p)
    sleep(50)
    networkManager.stopNetworkService()
