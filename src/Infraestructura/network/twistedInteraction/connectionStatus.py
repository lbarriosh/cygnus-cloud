# -*- coding: UTF8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: connectionStatus.py    
    Version: 3.0
    Description: connection status definitions
    
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

class ConnectionStatus(object):
    """
    These objects store a connection's status and allow its modification
    in a thread-safe manner.
    """
    def __init__(self, status):
        """
        Initializes the status using its argument.
        """
        self._status = status
        self.__semaphore = BoundedSemaphore(1)
        
    def get(self):
        """
        Returns the status value
        """
        return self._status
    
    def set(self, value):
        """
        Modifies the status.
        """
        with self.__semaphore :
            self._status = value