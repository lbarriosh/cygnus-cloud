# -*- coding: utf8 -*-
'''
Thread-safe counter definitions
@author: Luis Barrios Hernández
@version: 1.0
'''

from threading import BoundedSemaphore

class MultithreadingCounter(object):
    """
    A thred-safe counter.
    """
    def __init__(self):
        """
        Initializes the counter.
        Args:
            None
        """
        self.__semaphore = BoundedSemaphore(1)
        self.__counter = 0
        
    def read(self):
        """
        Retuns the counter's current value.
        Args:
            None
        Returns:
            The counter's current value
        """
        return self.__counter
    
    def increment(self):
        """
        Increments the counter.
        Args:
            None
        Returns:
            Nothing
        """
        with self.__semaphore:
            self.__counter += 1
            
    def decrement(self):
        """
        Decrements the counter.
        Args:
            None
        Returns:
            Nothing
        """
        with self.__semaphore:
            self.__counter -= 1
