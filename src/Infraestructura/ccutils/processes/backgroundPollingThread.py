# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: backgroundPollingThread.py    
    Version: 1.0
    Description: background processes thread definitions
    
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

class BackgroundProcessesPollingThread(BasicThread):
    """
    These threads will read the background processes' returned values
    """
    def __init__(self, processesList):
        """
        Initializes the thread's state
        Args:
            processesList: a background processes list
        """
        BasicThread.__init__(self, "Background processes polling thread")
        self.__processesList = processesList
        
    def run(self):
        # Run method, common to all threads        
        while not (self.finish() and self.__processesList.isEmpty()) :
            i = 0
            while (i < self.__processesList.getSize()) :
                result = self.__processesList[i].poll()
                if (result != None) :
                    self.__processesList.pop(i)
                i += 1
            sleep(0.1)