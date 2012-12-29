'''
Created on Dec 29, 2012

@author: luis
'''

from twisted.internet.protocol import Protocol, Factory

class SimpleProtocol(Protocol):
    
    def __init__(self, side):
        self.role = side
        self.connected = False
    
    def dataReceived(self, data):
        print self.role, ' - Received: ', data
        
    def connectionMade(self):
        print self.role, ' - Connection established'
        self.connected = True
        
    def connectionLost(self, reason):
        print self.role, ' Connection lost (', reason, ')'
        self.connected = False
        
    def isConnected(self):
        return self.connected
    
    def sendData(self, data):
        self.transport.write(data)
        
class SimpleProtocolFactory(Factory):
    def __init__(self, side):
        protocol = SimpleProtocol
        self.role = side
        self.instance = None
    
    def buildProtocol(self, addr):
        self.instance = SimpleProtocol(self.role)
        return self.instance
    
    def getInstance(self):
        return self.instance