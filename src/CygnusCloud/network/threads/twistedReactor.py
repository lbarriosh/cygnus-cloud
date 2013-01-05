'''
Created on Jan 5, 2013

@author: luis
'''

from twisted.internet import reactor
from threading import Thread

class _TwistedReactorThread(Thread):
    """
    These threads run the twisted reactor loop.
    @attention: Once the reactor is stopped, it won\'t be able to start again.
    """
    def __init__(self):
        Thread.__init__(self)
        
    def __workaround(self):
        reactor.callLater(1, self.__workaround)
    
    def run(self):        
        reactor.callLater(1, self.__workaround)
        reactor.run(installSignalHandlers=0)
        
    def stop(self):
        reactor.stop()  
