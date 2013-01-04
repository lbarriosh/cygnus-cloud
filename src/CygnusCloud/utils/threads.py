'''
Created on Jan 4, 2013

@author: luis
'''

from threading import Thread
from time import sleep

class BasicThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.__stop = False
        self.__isRunning = False
        
    def stopped(self):
        return self.__stop
    
    def start(self):
        if not self.__isRunning :
            Thread.start(self)
            self.__isRunning = True
    
    def stop(self):
        self.__stop = True
        self.__isRunning = False 

class QueueProcessingThread(BasicThread):
    """
    A class associated with a data processing thread.
    These threads read data from a queue and process
    them in an abstract way.
    """
    def __init__(self, queue):
        """
        Initializes the thread's state
        """
        BasicThread.__init__(self)        
        self.__queue = queue     
        
    def processElement(self, element):
        """
        Processes an element
        """
        pass
    
    def run(self):
        while not (self.stopped() and self.__queue.isEmpty()):
            while not self.__queue.isEmpty() :
                element = self.__queue.dequeue()
                self.processElement(element)
            if not self.stopped() :
                sleep(10) # Sleep for 10 milliseconds when there's nothing to do   