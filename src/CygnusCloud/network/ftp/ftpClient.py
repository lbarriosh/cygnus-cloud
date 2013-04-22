# # -*- coding: utf8 -*-
from ftplib import FTP
from time import sleep
import os

# from network.threads.twistedReactor import TwistedReactorThread
# from twisted.internet import reactor
# from network.ftp.twistedInteraction import FTPClientFactory
# from ftpException import FTPException
# 
# from time import sleep
# 
# class FTPClient(object):
#     def __init__(self, serverIP, serverPort, username, password):
#         self.__serverIP = serverIP
#         self.__serverPort = serverPort;
#         settings = {'user' : username, 'password' : password}
#         self.__factory = FTPClientFactory(settings)
#         self.__reactorThread = None
#         self.__transferringFile = False
#         self.__deferred = None
#         
#     def connect(self):        
#         if (not reactor.running) :
#             self.__reactorThread = TwistedReactorThread()
#             self.__reactorThread.start()
#         self.__iListeningPort = reactor.connectTCP(self.__serverIP, self.__serverPort, self.__factory)
#         while not self.__factory.isConnectionReady() :
#             sleep(0.1)
#         
#     def disconnect(self):
#         self.__factory.stopFactory()
#         
#     def storeFile(self, filePath):
#         if (self.__transferringFile) :
#             raise FTPException("There's another active transfer. You must wait for it to finish.")
#         self.__transferringFile = True
#         (self.__deferred, _unused) = self.__factory.getProtocol().storeFile(filePath, 0) 
#         self.__deferred.addCallback(self.__onTransferFinish)
#             
#     def __onTransferFinish(self):
#         self.__transferringFile = False
#         
#     def hasActiveTransferFinished(self):
#         return not self.__transferringFile
#     
#     def cancelActiveTransfer(self):
#         self.__deferred.cancel()
#         self.__transferringFile = False
#     
#     def retrieve(self, filePath):
#         pass
# 
# if __name__ == '__main__' :
#     ftpClient = FTPClient('192.168.0.4', 2121, 'cygnuscloud' , '12345')
#     ftpClient.connect()
#     ftpClient.storeFile("/home/luis/VMServer_settings.conf")
#     while not ftpClient.hasActiveTransferFinished() :
#         sleep(0.1)
#     print "***"
#     ftpClient.disconnect()

class FTPClient(object):
    def __init__(self):
        self.__ftp = FTP()
    
    def connect(self, host, port, timeout, user, password):
        self.__ftp.connect(host, port, timeout)
        self.__ftp.login(user, password)
        
    def storeFile(self, fileName, fileDirectory):
        self.__ftp.set_pasv(True)
        self.__ftp.storbinary("STOR " + fileName, open(fileDirectory + "/" + fileName, "rb"))
        file.close()
        
    def disconnect(self):
        self.__ftp.quit()
        
if __name__ == '__main__' :
    ftpClient = FTPClient()
    ftpClient.connect('192.168.0.4', 2121, 10, 'cygnuscloud' , '12345')
    ftpClient.storeFile("auth.txt", "/home/luis")
    ftpClient.disconnect()