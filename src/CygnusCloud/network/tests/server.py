# -*- coding: utf8 -*-
'''
A simple server test
@author: Luis Barrios Hernández
@version: 1.0
'''

from network.manager import NetworkManager
from network.tests.dummyCallback import DummyCallback
from time import sleep

if __name__ == "__main__" :
    networkManager = NetworkManager()
    networkManager.startNetworkService()
    print "Creating server..."
    networkManager.listenIn(8080, DummyCallback())
    print "The server is now ready"
    p = networkManager.createPacket(10)
    p.writeString("Hello, Client!")
    networkManager.sendPacket(8080, p)
    sleep(1000)
    networkManager.closeConnection(8080)
    networkManager.stopNetworkService()


