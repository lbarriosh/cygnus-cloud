# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: queueProcessingThread.py    
    Version: 1.5
    Description: queue processing thread class definitions
    
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

from ccutils.threads.basicThread import BasicThread
from time import sleep

class QueueProcessingThread(BasicThread):
    """
    These threads read elements from a queue and process them.
    """
    def __init__(self, threadName, queue):
        """
        Initializes the thread's state
        Args:
            queue: the queue to use
        """
        BasicThread.__init__(self, threadName)        
        self._queue = queue 
        
    def processElement(self, element):
        """
        Processes an element
        Args:
            element: the element to process
        Returns:
            Nothing
        """
        raise NotImplementedError
    
    def run(self):
        # Run method, common to all threads      
        while not (self.finish() and self._queue.isEmpty()):
            while not self._queue.isEmpty() :
                element = self._queue.dequeue()
                self.processElement(element)                
            sleep(0.01) # Sleep for 10 milliseconds when there's nothing to do   