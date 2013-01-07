'''
Created on Jan 6, 2013

@author: luis
'''

from utils.threads import BasicThread
from network.connection import CONNECTION_STATUS
from time import sleep

class _ConnectionMonitoringThread(BasicThread):
    def __init__(self, connectionPool):
        BasicThread.__init__(self)
        self.__connectionPool = connectionPool
        
    def run(self):
        while not (self.stopped() and self.__connectionPool.isEmpty()):           
            # Refresh the active connections
            connections = self.__connectionPool.values()
            for connection in connections :
                connection.refresh()
                if (connection.getStatus() == CONNECTION_STATUS.CLOSED) :
                    self.__connectionPool.pop(connection.getPort())
            sleep(0.1)
            
            
