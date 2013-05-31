'''
Created on Mar 29, 2013

@author: luis
'''

from ccutils.threads.basicThread import BasicThread
from time import sleep

class BackgroundProcessesPollingThread(BasicThread):
    def __init__(self, processesList):
        BasicThread.__init__(self, "Background processes polling thread")
        self.__processesList = processesList
        
    def run(self):
        while not (self.finish() and self.__processesList.isEmpty()) :
            i = 0
            while (i < self.__processesList.getSize()) :
                result = self.__processesList[i].poll()
                if (result != None) :
                    self.__processesList.pop(i)
                i += 1
            sleep(0.1)