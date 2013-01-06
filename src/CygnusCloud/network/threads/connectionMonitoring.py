'''
Created on Jan 6, 2013

@author: luis
'''

from utils.threads import BasicThread
from network.connection import CONNECTION_STATUS
from time import sleep

class _ConnectionMonitoringThread(BasicThread):
    def __init__(self, connectionPool, portList):
        BasicThread.__init__(self)
        self.__connectionPool = connectionPool
        self.__portList = portList
        
    def run(self):
        while not (self.stopped() and self.__connectionPool.isEmpty()):
            i = 0
            toDelete = []
            # Update connection status
            while i < self.__portList.getSize() :
                port = self.__portList[i]
                connection = self.__connectionPool[port]
                connection.refresh()
                if (connection.getStatus() == CONNECTION_STATUS.CLOSED) :
                    toDelete.append(port)
                i += 1
            # Delete the closed connections
            while not len(toDelete) == 0 :
                port = toDelete.pop()
                self.__connectionPool.pop(port)
                self.__portList.remove(port)           
            sleep(0.1)
            
            
