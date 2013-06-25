# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: multithreadingQueue.py    
    Version: 1.5
    Description: thread-safe queue definitions
    
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
from ccutils.dataStructures.multithreadingList import GenericThreadSafeList
from ccutils.dataStructures.queue import Queue

class GenericThreadSafeQueue(Queue):
    
    def __init__(self):
        """
        Creates an empty queue
        Args:
            None
        Returns:
            Nothing
        """
        self.__list = GenericThreadSafeList()
        
    def queue(self, element):
        """
        Adds an element to the queue
        Args:
            element: the element to consider
        Returns:
            Nothing
        """
        self.__list.append(element)
        
    def isEmpty(self):
        """
        Checks if the queue is empty
        Args:
            None
        Returns:
            True if the queue is empty and False if its not.
        """
        return self.__list.isEmpty()
        
    def dequeue(self):
        """
        Removes an element from the queue
        Args:
            None
        Returns:
            the removed element
        """
        return self.__list.pop(0)