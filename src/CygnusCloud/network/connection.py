# -*- coding: utf8 -*-
'''
Created on Jan 5, 2013

@author: luis
'''

class NetworkConnection(object):
    def __init__(self, isServer, port, protocol, queue, callback, incomingDataThread, deferred = None):
        self.__isServer = isServer
        self.__port = port
        self.__protocol = protocol
        self.__queue = queue
        self.__callback = callback
        self.__incomingDataThread = incomingDataThread
        self.__packagesToSend = 0
        self.__deferred = deferred
        self.__listeningPort = None
        self.__waitingThread = None
        self.__disposable = False
        
    def getPort(self):
        return self.__port
        
    def getQueue(self):
        return self.__queue
    
    def setWaitingThread(self, thread):
        self.__waitingThread = thread
    
    def sendPacket(self, p):
        self.__protocol.sendData(p)
        self.__packagesToSend -= 1
        
    def registerPacket(self):
        self.__packagesToSend += 1
    
    def setProtocol(self, protocol):
        self.__protocol = protocol
    
    def isReady(self):
        return self.__protocol != None
    
    def getCallback(self):
        return self.__callback
    
    def startThread(self):
        self.__incomingDataThread.start()
        
    def setListeningPort(self, listeningPort):
        print self.__listeningPort
    
    def stopThread(self, join):
        self.__incomingDataThread.stop()
        if join :
            self.__incomingDataThread.join()
            
    def isDisposable(self):
        return self.__disposable
    
    def close(self):
        if self.__isServer :
            if self.__listeningPort is None :
                # La conexión no se ha establecido todavía => cancelar deferred
                self.__deferred.cancel()
                self.__waitingThread.stop()
            else :
                deferred = self.__listeningPort.stopListenning()
                def setDisposable():
                    self.__disposable = True
                deferred.addCallback(setDisposable)
        else :
            self.__protocol.disconnect()
