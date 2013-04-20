# -*- coding: utf8 -*-

from network.threads.dataProcessing import QueueProcessingThread
from twisted.protocols.ftp import FTPClient
from twisted.internet.protocol import ClientCreator
from twisted.internet import reactor
from time import sleep

class FTPClientFactory():
    def p(self):
        pass

class SendQueue(QueueProcessingThread):
    def processElement(self, data):
        self.__finish = False
        def finish(ftpClient):
            self.__finish = True
            # Cuando acaba me desconecto
            ftpClient.quit()
        def connected(ftpClient):
            # Cuando me conecte le envío el archivo
            (sender, _connection) = ftpClient.storeFile(data['imagePath'])
            sender.addCallbacks(finish)
       
        # Creo el cliente FTP
        creator = ClientCreator(reactor, FTPClient, data['user'],
                            data['password'])
        # Me conecto al servidor
        creator.connectTCP(data['host'], int(data['port'])).addCallbacks(connected)
        reactor.run()
        
        # Espero a que acabe la transferencia
        while (not self.__finish) :
            sleep(10)

class RecieveQueue(QueueProcessingThread):
    
    def processElement(self, data):
        self.__finish = False
        def finish(ftpClient):
            print "recibido"
            self.__finish = True
            # Cuando acaba me desconecto
            ftpClient.quit()
        def connected(ftpClient):
            # Cuando me conecte pido el archivo
            future = ftpClient.retrieveFile(data['imagePath'], ftpClient)
            future.addCallbacks(finish)
       
        # Creo el cliente FTP
        creator = ClientCreator(reactor, FTPClient, data['user'],
                            data['password'], 0)
        # Me conecto al servidor
        creator.connectTCP(data['host'], int(data['port'])).addCallbacks(connected)
        reactor.run()
        
        # Espero a que acabe la transferencia
        while (not self.__finish) :
            sleep(10)
