# -*- coding: utf8 -*-
'''
Created on Apr 20, 2013

@author: luis
'''

from network.threads.twistedReactor import TwistedReactorThread
from twisted.internet import reactor
from network.ftp.twistedInteraction import FTPServerFactory
from network.interfaces.ipAddresses import get_ip_address

from time import sleep

class FTPServer(object):
    def __init__(self, listenningInterface, listenningPort, workingDirectory, allowedUsers, maxDownloadTransfers, maxUploadTransfers):
        settings = {'anonymousUserPath':'/dev/zero', 'authenticatedUserPath': workingDirectory, 'allowedUsers' : allowedUsers,
                    'maxDownloadTransfers' : maxDownloadTransfers, 'maxUploadTransfers' : maxUploadTransfers}
        self.__factory = FTPServerFactory(settings)
        self.__reactorThread = None
        self.__listenningInterface = listenningInterface
        self.__listenningPort = listenningPort
        self.__iListeningPort = None
        
    def startListenning(self):        
        if (not reactor.running) :
            self.__reactorThread = TwistedReactorThread()
            self.__reactorThread.start()
        self.__iListeningPort = reactor.listenTCP(self.__listenningPort, self.__factory, interface=get_ip_address(self.__listenningInterface))
        
    def stopListenning(self):
        # TODO: si salta algún error de twisted, registrar un handler para el deferred que devuelve la llamada al método 
        if (self.__iListeningPort != None) :
            self.__iListeningPort.stopListening()
        if (self.__reactorThread != None):
            self.__reactorThread.stop()

if __name__ == '__main__' :
    ftpServer = FTPServer('eth0', 2121, '/tmp', {'cygnuscloud' : '12345'}, 1, 1)
    ftpServer.startListenning()
    sleep(1000)
    ftpServer.stopListenning()