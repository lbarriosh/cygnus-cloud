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
    p = networkManager.createPacket(1)
    p.writeString("***")
    networkManager.sendPacket('', 8080, p)
    sleep(10)
    networkManager.stopNetworkService()


