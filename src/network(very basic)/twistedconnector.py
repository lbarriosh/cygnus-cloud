'''
Created on Dec 29, 2012

@author: luis
'''

from threading import Thread
from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint, TCP4ClientEndpoint

def message():
    print 'The reactor is running...'
    reactor.callLater(5, message)

class TwistedConnector(Thread):
    
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        print 'Starting reactor'
        reactor.callLater(5, message)
        reactor.run(installSignalHandlers=0)
        
    def stop(self):
        reactor.stop()
        
    def createServer(self, port, factory):
        endpoint = TCP4ServerEndpoint(reactor, port)
        endpoint.listen(factory)
        
    def createClient(self, host, port, timeout, factory):
        endpoint = TCP4ClientEndpoint(reactor, host, port, timeout, None)
        endpoint.connect(factory)
        
        
    
