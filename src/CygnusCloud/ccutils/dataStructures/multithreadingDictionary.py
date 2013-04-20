# -*- coding: utf8 -*-
'''
Thread-safe dictionary definitions.
@author: Luis Barrios Hernández
@version: 1.0
'''

from threading import BoundedSemaphore

class GenericThreadSafeDictionary :
    """
    A thread-safe dictionary.
    @attention: This objects are NOT iterable to avoid nasty iterator issues.
    @note: This class\' methods behave just like the dictionary ones. 
    """
    def __init__(self):        
        self.__semaphore = BoundedSemaphore(1)
        self.__dict = dict()
        
    def clear(self):
        with self.__semaphore :
            self.__dict.clear()
            
    def get(self, key, default = None):
        with self.__semaphore:
            self.__dict.get(key, default)
            
    def has_key(self, key):
        with self.__semaphore:
            return self.__dict.has_key(key)
        
    def keys(self):
        with self.__semaphore:
            return self.__dict.keys()
        
    def pop(self, key):
        with self.__semaphore:
            return self.__dict.pop(key)
        
    def removeElement(self, value):
        with self.__semaphore:
            targetKey = None
            for key in self.__dict.keys():
                if self.__dict[key] == value :
                    targetKey = key
                    break
            self.__dict.pop(targetKey)    
        
    def values(self):
        with self.__semaphore:
            return self.__dict.values()
        
    def isEmpty(self):
        with self.__semaphore:
            return len(self.__dict) == 0
        
    def getSize(self):
        with self.__semaphore:
            return len(self.__dict)
        
    def __getitem__(self, index):
        with self.__semaphore:
            return self.__dict.__getitem__(index)
        
    def __setitem__(self, key, value):
        with self.__semaphore:
            return self.__dict.__setitem__(key, value)