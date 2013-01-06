'''
Created on Jan 6, 2013

@author: luis
'''

from threading import BoundedSemaphore

class MultithreadingCounter(object):
    def __init__(self):
        self.__semaphore = BoundedSemaphore(1)
        self.__counter = 0
        
    def read(self):
        return self.__counter
    
    def increment(self):
        with self.__semaphore:
            self.__counter += 1
            
    def decrement(self):
        with self.__semaphore:
            self.__counter -= 1
