from twisted.protocols import ftp
from twisted.cred import portal, checkers, credentials
from twisted.internet import reactor
from ccutils.dataStructures.multithreadingCounter import MultithreadingCounter

class MaxConnectionsExceed(ftp.FTPCmdError):
    errorCode = ftp.CANT_OPEN_DATA_CNX
    
    def response(self):
        return ftp.RESPONSE[self.errorCode]
    
class FTPLimited(ftp.FTP):
    maxDown = 0
    maxUp = 0
    __downTransfers = MultithreadingCounter()
    __upTransfers = MultithreadingCounter()
    
    def ftp_STOR(self, path):
        def recieved(result):
            FTPLimited.__upTransfers.decrement()
            print "Transferido. Quedan " + str(FTPLimited.maxUp - FTPLimited.__upTransfers.read()) + " huecos."
        def failRecieved(result):
            pass
        if (FTPLimited.__upTransfers.incrementIfLessThan(FTPLimited.maxUp)):
            print "Transfiriendo. Quedan " + str(FTPLimited.maxUp - FTPLimited.__upTransfers.read()) + " huecos."
            response = ftp.FTP.ftp_STOR(self, path).addCallbacks(recieved, failRecieved)
            return response
        else:
            return ftp.defer.fail(MaxConnectionsExceed("Exceed max upload connection"))
        
    def ftp_RETR(self, path):
        def send(result):
            FTPLimited.__downTransfers.decrement()
            print "Transferido. Quedan " + str(FTPLimited.maxUp - FTPLimited.__upTransfers.read()) + " huecos."
        if (FTPLimited.__downTransfers.incrementIfLessThan(FTPLimited.maxDown)):
            print "Transfiriendo. Quedan " + str(FTPLimited.maxDown - FTPLimited.__downTransfers.read()) + " huecos."
            response = ftp.FTP.ftp_RETR(self, path).addCallbacks(send, send)
            return response
        else:
            return ftp.defer.fail(MaxConnectionsExceed("Exceed max download connection"))


class FTPRealmPath(ftp.FTPRealm):
    
    def __init__(self, anonymousPath, userPath):
        ftp.FTPRealm.__init__(self, anonymousPath, userPath)
        
    def getHomeDirectory(self, avatarId):
        return self.userHome
        
class FtpServerFactory(object):

    def __init__(self, config):
        f = ftp.FTPFactory()
        print ("Starting ftp server")
        p = portal.Portal(FTPRealmPath('./', '/home/saguma'))

        p.registerChecker(checkers.AllowAnonymousAccess(), credentials.IAnonymous)
        
        if config['allowed_users']:
            p.registerChecker(checkers.InMemoryUsernamePasswordDatabaseDontUse(**config['allowed_users']))

        f.portal = p
        f.allowAnonymous = False
        FTPLimited.maxDown = int(config["maxDownConection"])
        FTPLimited.maxUp = int(config["maxUpConection"])
        f.protocol = FTPLimited
        self.f = f
        self.port = int(config['port'])

    def makeListener(self):
        """
        Starts listening to a random port.
        @return: an object that provides L{IListeningPort}.
        """
        reactor.listenTCP(self.port, self.f, interface="127.0.0.1")
        reactor.run()

if __name__ == "__main__" :
    
        port = FtpServerFactory({'port':'2121','allowed_users': {'twisted':'twisted'}, 'maxDownConection' : '1','maxUpConection' : '1',}).makeListener()
        # important: use the addCleanup function instead of the normal tearDown function.
        print port
        while (True) :
            import time
            time.sleep(10)