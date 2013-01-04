'''
Created on Jan 4, 2013

@author: luis
'''

from threading import BoundedSemaphore

class GenericThreadSafeDictionary :
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
        
    def values(self):
        with self.__semaphore:
            return self.__dict.values()
        
    def __getitem__(self, index):
        with self.__semaphore:
            return self.__dict.__getitem__(index)
        
    def __setitem__(self, key, value):
        with self.__semaphore:
            return self.__dict.__setitem__(key, value)