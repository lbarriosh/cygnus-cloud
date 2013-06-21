# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: multithreadingCounter.py    
    Version: 2.0
    Description: thread-safe counter definitions
    
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

class MultithreadingCounter(object):
    """
    A thread-safe counter.
    """
    def __init__(self):
        """
        Initializes the counter
        Args:
            None
        """
        self.__semaphore = BoundedSemaphore(1)
        self.__counter = 0
        
    def read(self):
        """
        Reads the counter's current value
        Args:
            None
        Returns:
            The counter's current value
        """
        return self.__counter
    
    def increment(self):
        """
        Increments the counter
        Args:
            None
        Returns:
            Nothing
        """
        with self.__semaphore:
            self.__counter += 1
            
    def decrement(self):
        """
        Decrements the counter
        Args:
            None
        Returns:
            Nothing
        """
        with self.__semaphore:
            if (self.__counter == 0) :
                return
            self.__counter -= 1
    
    def incrementIfGreaterThan(self, n):
        """
        Increments the counter if its value is greater than a given
            threshold
        Args:
            n: the threshold to consider
        Returns:
            True if the counter was incremented, and False
            otherwise.
        """
        with self.__semaphore:
            if (self.__counter > n):
                self.__counter += 1
                return True
            else :
                return False
            
    def decrementIfGreaterThan(self, n):
        """
        Decrements the counter if its value is greater than a given
            threshold
        Args:
            n: the threshold to consider
        Returns:
            True if the counter was decremented, and False
            otherwise.
        """
        with self.__semaphore:
            if (self.__counter > n):
                self.__counter -= 1
                return True
            else :
                return False
            
    def decrementIfLessThan(self, n):
        """
        Decrements the counter if its value is less than a given
            threshold
        Args:
            n: the threshold to consider
        Returns:
            True if the counter was decremented, and False
            otherwise.
        """
        with self.__semaphore:
            if (self.__counter < n):
                self.__counter -= 1
                return True
            else :
                return False