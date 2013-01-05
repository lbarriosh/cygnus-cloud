# -*- coding: utf8 -*-
'''
Created on Jan 4, 2013

@author: luis
'''

from twisted.internet import reactor
from utils.threads import QueueProcessingThread, BasicThread
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
                
class _IncomingDataThread(QueueProcessingThread):
    """
    A class associated with the incoming packages threads.
    This threads will process the incoming packages.
    """
    def __init__(self, queue, callbackObject):
        QueueProcessingThread.__init__(self, queue)   
        self.__callbackObject = callbackObject     
        
    def processElement(self, e):
        self.__callbackObject.processPacket(e)
        
class _OutgoingDataThread(QueueProcessingThread):
    def processElement(self, e):
        (connection, packet) = e
        connection.sendPacket(packet)
        
class _ServerWaitThread(BasicThread):
    
    def __init__(self, factory, registerMethod, startThreadMethod):
        BasicThread.__init__(self)        
        self.__factory = factory
        self.__registerMethod = registerMethod
        self.__startThreadMethod = startThreadMethod
        
    def run(self): 
        while not self.stopped() and self.__factory.getInstance() == None :
            sleep(0.01)
        if not self.stopped() :
            self.__registerMethod(self.__factory.getInstance())
            self.__startThreadMethod() 