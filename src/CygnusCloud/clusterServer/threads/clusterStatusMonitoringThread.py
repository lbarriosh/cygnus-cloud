'''
Created on Apr 11, 2013

@author: luis
'''

from ccutils.threads import BasicThread

from time import sleep

class ClusterStatusMonitoringThread(BasicThread):
    
    def __init__(self, updateHandler, sleepTime):
        BasicThread.__init__(self, "Cluster status update thread")
        self.__updateHandler = updateHandler
        self.__sleepTime = sleepTime
        
    def run(self):
        while not self.finish() :
            self.__updateHandler.sendStatusRequestPacketsToClusterMachines()
            sleep(self.__sleepTime)
