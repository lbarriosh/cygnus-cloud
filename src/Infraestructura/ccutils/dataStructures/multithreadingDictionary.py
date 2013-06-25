# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: multithreadingDictionary.py    
    Version: 2.0
    Description: thread-safe dictionary definitions
    
    Copyright 2012-13 Luis Barrios Hernández, Adrián Fernández Hernández,
        Samuel Guayerbas Martín

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

from threading import BoundedSemaphore

class GenericThreadSafeDictionary :
    """
    A thread-safe dictionary.
    @attention: In order to avoid nasty iterator issues, these objects are NOT iterable.
    """
    def __init__(self):      
        """
        Creates an empty dictionary
        Args:
            None
        """  
        self.__semaphore = BoundedSemaphore(1)
        self.__dict = dict()
        
    def clear(self):
        """
        Deletes the dictionary's content
        Args:
            None
        Returns:
            Nothing
        """
        with self.__semaphore :
            self.__dict.clear()
            
    def get(self, key, default = None):
        """
        Returns the value associated with a key
        Args:
            key: the key to consider
            default: the value to return when the key does not exist.
        Returns:
            the value associated with the key.
        """
        with self.__semaphore:
            self.__dict.get(key, default)
            
    def has_key(self, key):
        """
        Checks if the dictionary contains a key.
        Args:
            key: the key to consider
        Returns:
            True if the dictionary stores the key, and False otherwise.
        """
        with self.__semaphore:
            return self.__dict.has_key(key)
        
    def keys(self):
        """
        Returns all the keys stored in the dictionary.
        Args:
            None
        Returns: A list with all the keys stored in the dictionary
        """
        with self.__semaphore:
            return self.__dict.keys()
        
    def pop(self, key):
        """
        Removes a (key, value) pair from the dictionary.
        Args:
            key: the key to consider
        Returns:
            Nothing
        """
        with self.__semaphore:
            return self.__dict.pop(key)
        
    def removeElement(self, value):
        """
        Removes a (key, value) pair from the dictionary
        Args:
            value: the value to consider
        Returns:
            Nothing
        """
        with self.__semaphore:
            targetKey = None
            for key in self.__dict.keys():
                if self.__dict[key] == value :
                    targetKey = key
                    break
            self.__dict.pop(targetKey)    
        
    def values(self):
        """
        Returns all the values stored in the dictionary.
        Args:
            None
        Returns: A list with all the values stored in the dictionary
        """
        with self.__semaphore:
            return self.__dict.values()
        
    def isEmpty(self):
        """
        Checks if the dictionary is empty
        Args:
            None
        Returns:
            True if the dictionary is empty, and False if it's not.
        """
        with self.__semaphore:
            return len(self.__dict) == 0
        
    def getSize(self):
        """
        Returns the dictionary's size
        Args:
            None
        Returns:
            The dictionary's size
        """
        with self.__semaphore:
            return len(self.__dict)
        
    def __getitem__(self, index):
        # Operator [] in expression
        with self.__semaphore:
            return self.__dict.__getitem__(index)
        
    def __setitem__(self, key, value):
        # Operator[] at left side of assignment operation
        with self.__semaphore:
            return self.__dict.__setitem__(key, value)