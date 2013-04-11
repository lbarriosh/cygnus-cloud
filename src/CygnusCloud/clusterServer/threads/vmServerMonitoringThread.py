'''
Created on Apr 11, 2013

@author: luis
'''

from ccutils.threads import BasicThread

from time import sleep

class VMServerMonitoringThread(BasicThread):
    
    def __init__(self, updateHandler, sleepTime):
        BasicThread.__init__(self, "VM server status update thread")
        self.__updateHandler = updateHandler
        self.__sleepTime = sleepTime
        
    def run(self):
        while not self.finish() :
            self.__updateHandler.sendStatusRequestPacketsToActiveVMServers()
            sleep(self.__sleepTime)
