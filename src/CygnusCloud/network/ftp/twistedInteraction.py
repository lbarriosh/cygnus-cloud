# -*- coding: utf8 -*-
from twisted.protocols import ftp
from twisted.internet.protocol import Protocol
from twisted.cred import portal, checkers, credentials
from ccutils.dataStructures.multithreadingCounter import MultithreadingCounter

class ConnectionLimitExceeded(ftp.FTPCmdError):
    errorCode = ftp.CANT_OPEN_DATA_CNX
    
    def response(self):
        return ftp.RESPONSE[self.errorCode]
    
class FTPServerProtocol(ftp.FTP):   
        
    def __init__(self, downloadTransfersCounter, uploadTransfersCounter):
        self.__downloadTransfersCounter = downloadTransfersCounter
        self.__uploadTransfersCounter = uploadTransfersCounter
    
    def ftp_STOR(self, path):
        def recieved(result):
            self.__uploadTransfersCounter.decrement()
            print "Transferido. Quedan " + str(self.__uploadTransfersCounter.getMaxValue() - self.__uploadTransfersCounter.read()) + " huecos."
        def failRecieved(result):
            pass
        print "Huecos subida = "+str(self.__uploadTransfersCounter.read())
        if (self.__uploadTransfersCounter.incrementIfLessThanLimit()):
            print "Transfiriendo. Quedan " + str(self.__uploadTransfersCounter.getMaxValue() - self.__uploadTransfersCounter.read()) + " huecos."
            response = ftp.FTP.ftp_STOR(self, path).addCallbacks(recieved, failRecieved)
            return response
        else:
            return ftp.defer.fail(ConnectionLimitExceeded("The upload transfers limit has been reached"))
        
    def ftp_RETR(self, path):
        print "Huecos bajada = "+str(self.__downloadTransfersCounter.read())
        def send(result):
            self.__downloadTransfersCounter.decrement()
            print "Transferido. Quedan " + str(self.__downloadTransfersCounter.getMaxValue() - self.__downloadTransfersCounter.read()) + " huecos."
        if (self.__downloadTransfersCounter.incrementIfLessThanLimit()):
            print "Transfiriendo. Quedan " + str(self.__downloadTransfersCounter.getMaxValue() - self.__downloadTransfersCounter.read()) + " huecos."
            response = ftp.FTP.ftp_RETR(self, path).addCallbacks(send, send)
            return response
        else:
            return ftp.defer.fail(ConnectionLimitExceeded("The download transfers limit has been reached"))

    def getFreeUpSlot(self):
        return self.__uploadTransfersCounter.getMaxValue() - self.__uploadTransfersCounter.read()
    def getFreeDownSlot(self):
        return self.__downloadTransfersCounter.getMaxValue() - self.__downloadTransfersCounter.read()
        

class FTPRealmPath(ftp.FTPRealm):
    
    def __init__(self, anonymousPath, userPath):
        ftp.FTPRealm.__init__(self, anonymousPath, userPath)
        
    def getHomeDirectory(self, avatarId):
        return self.userHome
        
class FTPServerFactory(ftp.FTPFactory):

    def __init__(self, settings):
        print("Initializing FTP server")
        
        p = portal.Portal(FTPRealmPath(settings['anonymousUserPath'], settings['authenticatedUserPath']))
        p.registerChecker(checkers.AllowAnonymousAccess(), credentials.IAnonymous)        
        p.registerChecker(checkers.InMemoryUsernamePasswordDatabaseDontUse(**settings['allowedUsers']))
        self.portal = p
                
        self.__downloadTransfers = MultithreadingCounter(settings["maxDownloadTransfers"])
        self.__uploadTransfers = MultithreadingCounter(settings["maxUploadTransfers"])
        
        self.allowAnonymous = False
        self.protocol = FTPServerProtocol
        self.protocol.factory = self
        self.protocol.portal = p
        
    def buildProtocol(self, addr):
        return self.protocol(self.__downloadTransfers, self.__uploadTransfers)
        
    def doStart(self):
        pass