# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: commandsMonitoringThread.py    
    Version: 2.0
    Description: cluster endpoint daemon commands monitoring thread
    
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

class CommandsMonitoringThread(BasicThread):
    """
    These threads will monitor all the commands' execution, generating timeout errors when
    necessary
    """
    def __init__(self, commandsDBConnector, commandTimeout, commandsHandler, sleepTime):
        """
        Initializes the thread's state
        Args:
            commandsDBConnector: a commands database connector
            commandTimeout: the timeout to use (in seconds)
            commandsHandler: the commands handler object to use
            sleepTime: the sleep time between two consecutive updates (in seconds)
        """
        BasicThread.__init__(self, "Command monitoring thread")
        self.__commandsDBConnector = commandsDBConnector
        self.__commandTimeout = commandTimeout
        self.__commandsHandler = commandsHandler
        self.__sleepTime = sleepTime
        
    def run(self):
        while not self.finish() :
            commandIDs = self.__commandsDBConnector.removeOldCommands(self.__commandTimeout)
            if (len(commandIDs) != 0) :
                (outputType, commandOutput) = self.__commandsHandler.createCommandTimeoutErrorOutput()
                for commandID in commandIDs :
                    self.__commandsDBConnector.addCommandOutput(commandID, outputType, commandOutput, True)
            sleep(self.__sleepTime)