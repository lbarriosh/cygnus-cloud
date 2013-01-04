'''
Created on Jan 4, 2013

@author: luis
'''

from twisted.internet import reactor
from threading import Thread
from time import sleep

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
        
class _IncomingDataThread(Thread):
    """
    A class associated to the incoming packages threads.
    This threads will process the incoming packages.
    """
    def __init__(self, queue, callbackObject):
        """
        Initializes the thread's state
        """
        Thread.__init__(self)
        self.__stop = False
        self.__queue = queue
        self.__isRunning = False
        self.__callbackObject = callbackObject
        
    def start(self):
        if not self.__isRunning :
            Thread.start(self)
            self.__isRunning = True
    
    def stop(self):
        self.__stop = True
        
    def run(self):
        while not (self.__stop and self.__queue.isEmpty()):
            while not self.__queue.isEmpty() :
                packet = self.__queue.dequeue()
                self.__callbackObject.processPacket(packet)
            if not self.__stop :
                sleep(10) # Sleep for 10 milliseconds when there's nothing to do   
