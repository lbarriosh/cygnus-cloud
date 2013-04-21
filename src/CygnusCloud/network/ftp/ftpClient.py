# -*- coding: utf8 -*-
from network.threads.twistedReactor import TwistedReactorThread
from twisted.internet import reactor
from network.ftp.twistedInteraction import FTPClientFactory

from time import sleep

class FTPClient(object):
    def __init__(self, serverIP, serverPort, username, password):
        self.__serverIP = serverIP
        self.__serverPort = serverPort;
        settings = {'user' : username, 'password' : password}
        self.__factory = FTPClientFactory(settings)
        self.__reactorThread = None
        
    def connect(self):        
        if (not reactor.running) :
            self.__reactorThread = TwistedReactorThread()
            self.__reactorThread.start()
        self.__iListeningPort = reactor.connectTCP(self.__serverIP, self.__serverPort, self.__factory)
        
    def disconnect(self):
        self.__factory.stopFactory()

if __name__ == '__main__' :
    ftpServer = FTPClient('192.168.1.3', 2121, 'cygnuscloud' , '12345')
    ftpServer.connect()
    while (True) :
        sleep(1000)
    ftpServer.disconnect()