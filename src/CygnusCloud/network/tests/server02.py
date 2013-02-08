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
    networkManager = NetworkManager()
    networkManager.startNetworkService()
    networkManager.listenIn(8080, DummyCallback())
    networkManager.closeConnection('', 8080)
    sleep(5)
    try :
        networkManager.listenIn(8080, DummyCallback())
    except Exception as e:
        print e
    print 'Finising'
    networkManager.stopNetworkService()