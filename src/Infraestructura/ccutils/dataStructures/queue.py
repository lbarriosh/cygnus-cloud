# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: queue.py    
    Version: 1.0
    Description: Queue interface definitions
    
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
class Queue(object):
    """
    This class defines the interface used by all the queues.
    """
           
    def isEmpty(self):
        """
        Checks if the queue is empty
        Args:
            None
        Returns:
            True if the queue is empty and False if its not.
        """
        raise NotImplementedError
        
    def dequeue(self):
        """
        Removes an element from the queue
        Args:
            None
        Returns:
            the removed element
        """
        raise NotImplementedError