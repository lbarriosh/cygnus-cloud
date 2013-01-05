'''
Created on Jan 5, 2013

@author: luis
'''

from utils.threads import BasicThread
from time import sleep

class _ClosedConnectionThread(BasicThread):
    def __init__(self, connectionList, portList):
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
