# -*- coding: UTF8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: twistedReactor.py    
    Version: 1.5
    Description: twisted reactor thread definitions
    
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

from twisted.internet import reactor
from threading import Thread

class TwistedReactorThread(Thread):
    """
    These threads run the twisted reactor loop.
    @attention: Once the reactor is stopped, it won't be able to start again.
    """
    def __init__(self):
        """
        Initializes the thread's state.
        Args:
            None
        Returns:
            Nothing
        """
        Thread.__init__(self, name="Twisted reactor thread")
        
    def __workaround(self):
        """
        This is a workaround to fix a nasty Twisted bug. 
        Args:
            None
        Returns:
            Nothing
        """
        reactor.callLater(1, self.__workaround)
    
    def run(self):        
        """
        Starts and runs the twisted reactor loop.
        Args:
            None
        Returns:
            Nothing
        """
        reactor.callLater(1, self.__workaround)
        reactor.run(installSignalHandlers=0)
        
    def stop(self):
        """
        Stops the twisted reactor loop
        Args:
            None
        Returns:
            Nothing
        """
        reactor.stop()  