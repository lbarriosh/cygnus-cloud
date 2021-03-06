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
    networkManager.listenIn(8081, DummyCallback(), True)
    print "The server is now ready"
    sleep(30)
    print networkManager.isConnectionReady('',8080)
    p = networkManager.createPacket(10)
    p.writeString("Hello, Client!")
    networkManager.sendPacket('', 8080, p)
    p = networkManager.createPacket(10)
    sleep(10)
    p.writeString("Hello, Client 1!")
    networkManager.sendPacket('', 8081, p)
    print "Packet sent from server"
    networkManager.stopNetworkService()


