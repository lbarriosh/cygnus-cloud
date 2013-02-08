# -*- coding: utf8 -*-
'''
Status database update thread definitions
@author: Luis Barrios Hernández
@version: 1.0
'''


    
from time import sleep
from utils1.threads import BasicThread

class UpdateHandler(object):
    def sendUpdateRequestPackets(self):
        raise NotImplementedError

class StatusDatabaseUpdateThread(BasicThread):
    def __init__(self, updateHandler, sleepTime):
        BasicThread.__init__(self)
        self.__handler = updateHandler
        self.__sleepTime = sleepTime

    def run(self):
        while not self.stopped() :
            self.__handler.sendUpdateRequestPackets()
            sleep(self.__sleepTime)
