# -*- coding: UTF8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: connectionMonitoring.py    
    Version: 3.6
    Description: connection monitoring thread definitions
    
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
from network.twistedInteraction.connection import CONNECTION_STATUS
from time import sleep

class ConnectionMonitoringThread(BasicThread):
    """
    These threads will refresh all the network connections periodically
    and will remove the closed connections from the connection pool.
    """
    def __init__(self, connectionPool):
        """
        Initializes the thread's state.
        """
        BasicThread.__init__(self, "Connection monitoring thread")
        self.__connectionPool = connectionPool
        
    def run(self):
        """
        Refreshes all the network connections until the thread must stop
        and there are no more connections to refresh.
        """
        while not (self.finish() and self.__connectionPool.isEmpty()):        
            # Refresh the active connections
            connections = self.__connectionPool.values()
            for connection in connections :
                connection.refresh()
                if (connection.getStatus() == CONNECTION_STATUS.CLOSED) :
                    self.__connectionPool.pop((connection.getHost(), connection.getPort()))
            sleep(1)