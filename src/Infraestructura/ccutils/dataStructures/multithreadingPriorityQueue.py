# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: multithreadingPriorityQueue.py    
    Version: 1.5
    Description: thread-safe priority definitions
    
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
from ccutils.dataStructures.queue import Queue

class GenericThreadSafePriorityQueueException(Exception):
    """
    Thread-safe priority queue exception class
    """
    pass

class GenericThreadSafePriorityQueue(Queue):
    """
    A thread-safe priority queue
    @attention: In order to avoid nasty iterator issues, these objects are NOT iterable.    
    """
    def __init__(self):
        """
        Creates an empty priority queue
        Args:
            None
        Returns:
            Nothing
        """
        self._data = dict()
        # We use a semaphore to avoid compilation problems in Python 3.x
        self.__semaphore = BoundedSemaphore(1) 
        self.__elements = 0
        
    def queue(self, priority, data):
        """
        Adds a new element to the queue
        Args:
            priority: an integer priority value.
            data: the data to add to the queue
        Returns:
            Nothing
        """
        # Check arguments
        if not isinstance(priority, int) :
            raise GenericThreadSafePriorityQueueException("The priority must be an integer value")
        # Acquire semaphore, add data
        with self.__semaphore:
            if not self._data.has_key(priority) :
                self._data[priority] = []       
            self._data[priority].append(data)
            self.__elements += 1
            
    def dequeue(self):
        """
        Pops an element from the queue.
        Args:
            None
        Returns:
            The popped element.
        """
        with self.__semaphore:
            if self.__elements == 0:
                raise GenericThreadSafePriorityQueueException("The queue is empty")
            keys = self._data.keys()
            keys.sort() # This is the little price to pay for an efficient queue operation. If the number of keys 
                        # remains constant, this operation has an O(1) time complexity.
            self.__elements -= 1
            for key in keys:
                if not len(self._data[key]) == 0 :
                    return self._data[key].pop(0)
    
    def isEmpty(self):
        """
        Checks if the queue is empty
        Args:
            None
        Returns:
            True if the queue is empty and False if its not.
        """
        with self.__semaphore:
            return self.__elements == 0