# -*- coding: utf8 -*-
from twisted.protocols import ftp
from twisted.cred import portal, checkers, credentials
from ccutils.dataStructures.multithreadingCounter import MultithreadingCounter

class MaxConnectionsExceed(ftp.FTPCmdError):
    errorCode = ftp.CANT_OPEN_DATA_CNX
    
    def response(self):
        return ftp.RESPONSE[self.errorCode]
    
class FTPProtocol(ftp.FTP):   
        
    def __init__(self, downloadTransfersCounter, uploadTransfersCounter):
        self.__downloadTransfersCounter = downloadTransfersCounter
        self.__uploadTransfersCounter = uploadTransfersCounter
    
    def ftp_STOR(self, path):
        def recieved(result):
            self.__uploadTransfers.decrement()
            print "Transferido. Quedan " + str(self.__uploadTransfers.getMaxValue() - self.__uploadTransfers.read()) + " huecos."
        def failRecieved(result):
            pass
        if (self.__uploadTransfers.incrementIfLessThan(self.maxUploadTransfers)):
            print "Transfiriendo. Quedan " + str(self.__uploadTransfers.getMaxValue() - self.__uploadTransfers.read()) + " huecos."
            response = ftp.FTP.ftp_STOR(self, path).addCallbacks(recieved, failRecieved)
            return response
        else:
            return ftp.defer.fail(MaxConnectionsExceed("Exceeded max upload connection"))
        
    def ftp_RETR(self, path):
        def send(result):
            self.__downloadTransfers.decrement()
            print "Transferido. Quedan " + str(self.__downloadTransfersCounter.getMaxValue() - self.__uploadTransfers.read()) + " huecos."
        if (self.__downloadTransfers.incrementIfLessThan(self.__downloadTransfersCounter.getMaxValue())):
            print "Transfiriendo. Quedan " + str(self.__downloadTransfersCounter.getMaxValue() - self.__downloadTransfers.read()) + " huecos."
            response = ftp.FTP.ftp_RETR(self, path).addCallbacks(send, send)
            return response
        else:
            return ftp.defer.fail(MaxConnectionsExceed("Exceeded max download connection"))


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
        self.protocol = FTPProtocol
        
    def buildProtocol(self, addr):
        return self.protocol(self.__downloadTransfers, self.__uploadTransfers)
        
    def doStart(self):
        pass

class FTPClientFactory(ftp._PassiveConnectionFactory):

    def __init__(self, settings):
        print("Initializing FTP Client")
        self.__user = settings['user']
        self.__password = settings['password']
        self.protocol = ftp.FTPClient
        
    def buildProtocol(self, addr):
        return self.protocol(self.__user, self.__password)
        
    def doStart(self):
        pass