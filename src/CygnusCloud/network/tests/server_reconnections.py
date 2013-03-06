# -*- coding: utf8 -*-
'''
A simple server test
@author: Luis Barrios Hernández
@version: 1.0
'''

from network.manager.networkManager import NetworkManager
from network.tests.dummyCallback import DummyCallback
from time import sleep

if __name__ == "__main__" :
    networkManager = NetworkManager("/home/luis/Certificates")
    networkManager.startNetworkService()
    print "Creating server..."
    networkManager.listenIn(8080, DummyCallback(), True)
    print "The server is now ready"
    sleep(20)
    networkManager.closeConnection('', 8080)
    print "The server has closed the connetion"
    networkManager.listenIn(8080, DummyCallback(), True)
    p = networkManager.createPacket(10)
    p.writeString("Hello, Client!")
    networkManager.sendPacket('', 8080, p)
    p = networkManager.createPacket(10)
    networkManager.stopNetworkService()


