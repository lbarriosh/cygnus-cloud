# -*- coding: utf8 -*-
'''
Closed connection thread definitions.
@author: Luis Barrios Hernández
@version: 1.5
'''

from utils.threads import BasicThread
from time import sleep

class _ClosedConnectionThread(BasicThread):
    """
    This threads will check when a connection is safely closed.
    """
    def __init__(self, connectionList, portList):
        """
        Initializes this thread's state.
        Args:
            connectionList: a closed connection list.
            portList: a closed connection port list.
        """
        BasicThread.__init__(self)        
        self.__connectionList = connectionList
        self.__portList = portList
        
    def run(self):
        while not self.stopped():
            top = self.__connectionList.getSize()
            i = 0
            toDelete = []
            while i < top:
                c = self.__connectionList[i]
                if (c.isDisposable()):
                    toDelete.append(c)
                i += 1
            while len(toDelete) != 0 :
                c = toDelete.pop()
                self.__connectionList.remove(c)
                self.__portList.remove(c.getPort())
            sleep(0.01)
