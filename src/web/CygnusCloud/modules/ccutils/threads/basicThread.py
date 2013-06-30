# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: basicThread.py    
    Version: 1.5
    Description: base thread class definitions
    
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
from threading import Thread

class BasicThread(Thread):
    """
    Base class for all the stoppable threads
    """
    def __init__(self, threadName):
        """
        Initializes the thread's state.
        Args:
            threadName: the new thread's name
        """
        Thread.__init__(self, name=threadName)
        self.__stop = False
        self.__isRunning = False
        
    def finish(self):
        """
        Checks if this thread must finish or not.
        Args:
            None
        Returns:
            True if this thread must finish, and False otherwise.
        """
        return self.__stop
    
    def start(self):
        """
        Starts this thread
        Args:
            None
        Returns:
            Nothing
        """
        if not self.__isRunning :
            Thread.start(self)
            self.__isRunning = True
    
    def stop(self):
        """
        Sends a stop request to this thread.
        Args:
            None
        Returns:
            Nothing
        """
        self.__stop = True
        self.__isRunning = False 