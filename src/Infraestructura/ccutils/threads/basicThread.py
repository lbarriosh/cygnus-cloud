'''
Created on May 31, 2013

@author: luis
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