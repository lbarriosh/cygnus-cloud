# -*- coding: utf8 -*-
'''
Connection monitoring thread definitions.
@author: Luis Barrios Hernández
@version: 3.5
'''

from ccutils.threads import BasicThread
from network.twistedInteraction.connection import CONNECTION_STATUS
from time import sleep

class _ConnectionMonitoringThread(BasicThread):
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
                    self.__connectionPool.pop((connection.getIPAddress(), connection.getPort()))
            sleep(1)