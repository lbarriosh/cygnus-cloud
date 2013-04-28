# -*- coding: utf8 -*-
'''
Basic thread class definitions.
@author: Luis Barrios Hernández
@version: 1.2
'''

from threading import Thread
from time import sleep

class BasicThread(Thread):
    """
    A class for a stoppable thread.
    """
    def __init__(self, threadName):
        """
        Initializes the thread's state.
        Args:
            None
        """
        Thread.__init__(self, name=threadName)
        self.__stop = False
        self.__isRunning = False
        
    def finish(self):
        """
        Checks if this thread must finish or not.
        Args:
            None
        Returns:
            True if this thread must finish, and false otherwise.
        """
        return self.__stop
    
    def start(self):
        """
        Starts this thread
        Args:
            None
        Returns:
            Nothing
        """
        if not self.__isRunning :
            Thread.start(self)
            self.__isRunning = True
    
    def stop(self):
        """
        Sends a stop request to this thread.
        Args:
            None
        Returns:
            Nothing
        """
        self.__stop = True
        self.__isRunning = False 

class QueueProcessingThread(BasicThread):
    """
    A class associated with a data processing thread.
    These threads read data from a queue and process
    them in an abstract way.
    """
    def __init__(self, threadName, transferQueue):
        """
        Initializes the thread's state
        Args:
            transferQueue: the transferQueue to monitor.
        """
        BasicThread.__init__(self, threadName)        
        self._queue = transferQueue   
        
    def processElement(self, element):
        """
        Processes an element
        Args:
            element: the element to process
        Returns:
            Nothing
        """
        raise NotImplementedError
    
    def run(self):
        """
        Processes the queue until it's empty and the thread is finish.
        """        
        while not (self.finish() and self._queue.isEmpty()):
            while not self._queue.isEmpty() :
                element = self._queue.dequeue()
                self.processElement(element)      
            if (self.finish()) :
                print "Empty queue!"    
            sleep(0.01) # Sleep for 10 milliseconds when there's nothing to do   