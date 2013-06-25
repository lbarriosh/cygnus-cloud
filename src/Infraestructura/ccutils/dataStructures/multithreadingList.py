# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: multithreadingList.py    
    Version: 2.0
    Description: thread-safe list definitions
    
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

class GenericThreadSafeList :
    """
    A thread-safe list.
    @attention: in order to avoid nasty iterator issues, these objects are NOT iterable.
    """
    def __init__(self):
        """
        Creates an empty list
        Args:
            None
        """
        self.__semaphore = BoundedSemaphore(1)
        self._data = []
    
    def append(self, value):
        """
        Inserts a value at the end of the list
        Args:
            value: the value to add
        Returns:
            Nothing
        """
        with self.__semaphore:
            if self._data.count(value) == 0:
                self._data.append(value)
        
    def count(self, value):
        """
        Counts a value's appearances on the list.
        Args:
            the value to consider
        Returns:
            the value's appeareances on the list.            
        """
        with self.__semaphore:
            return self._data.count(value)
        
    def isEmpty(self):
        """
        Checks if the list is empty
        Args:
            None
        Returns:
            True if the list is empty, and False if it isn't.
        """
        with self.__semaphore:
            return len(self._data) == 0
        
    def index(self, n):
        """
        Returns the n-th value of the list.
        Args:
            n: the position to consider
        Returns:
            the n-th value of the list
        """
        with self.__semaphore:
            return self._data.index(n)
        
    def insert(self, index, value):
        """
        Inserts a value on the list
        Args:
            index: the position to consider
            value: the value to insert
        Returns:
            Nothing
        """
        with self.__semaphore:
            return self._data.insert(index, value)
        
    def pop(self, n):
        """
        Removes the n-th from the list and returns it.
        Args:
            n: the position to consider
        Returns:
            the n-th element of the list
        """
        with self.__semaphore:
            return self._data.pop(n)
        
    def remove(self, n):
        """
        Removes the n-th value from the list
        Args:
            n: the position to consider
        Returns:
            Nothing
        """
        with self.__semaphore :
            self._data.remove(n)
            
    def reverse(self):
        """
        Inverts the list
        Args:
            None
        Returns:
            Nothing
        """
        with self.__semaphore :
            self._data.reverse()
    
    def __getitem__(self, index):
        # Operator [] in expression
        with self.__semaphore:
            return self._data.__getitem__(index)
        
    def __setitem__(self, index, value):
        # # Operator[] at left side of assignment operation
        with self.__semaphore:
            return self._data.__setitem__(index, value)
        
    def getSize(self):
        """
        Returns the list's size
        Args:
            None
        Returns:
            the list's size
        """
        with self.__semaphore:
            return len(self._data)   