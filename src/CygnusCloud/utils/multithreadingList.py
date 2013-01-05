# -*- coding: utf8 -*-
'''
Created on Jan 5, 2013

@author: luis
'''

from threading import BoundedSemaphore

class GenericThreadSafeList :
    def __init__(self):
        self.__semaphore = BoundedSemaphore(1)
        self.__data = []
    
    def append(self, value):
        with self.__semaphore:
            self.__data.append(value)
        
    def count(self, value):
        with self.__semaphore:
            return self.__data.count(value)
        
    def index(self, value):
        with self.__semaphore:
            return self.__data.index(value)
        
    def insert(self, index, value):
        with self.__semaphore:
            return self.__data.insert(index, value)
        
    def pop(self, index):
        with self.__semaphore:
            return self.__data.pop(index)
        
    def remove(self, value):
        with self.__semaphore :
            self.__data.remove(value)
            
    def reverse(self, value):
        with self.__semaphore :
            self.__data.reverse()
    
    def __getitem__(self, index):
        with self.__semaphore:
            return self.__data.__getitem__(index)
        
    def __setitem__(self, index, value):
        with self.__semaphore:
            return self.__data.__setitem__(index, value)
        
    def getSize(self):
        with self.__semaphore:
            return len(self.__data)
    
