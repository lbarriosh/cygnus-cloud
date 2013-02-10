# -*- coding: utf8 -*-
'''
Status database update thread definitions
@author: Luis Barrios Hernández
@version: 1.1
'''

from utils.threads import BasicThread

from time import sleep

class UpdateHandler(object):
    """
    This class defines the interface used to perform the status database's
    periodic update.
    """
    def sendUpdateRequestPackets(self):
        """
        Sends the update request packets to the virtual machine servers
        Args:
            None
        Returns:
            Nothing
        """
        raise NotImplementedError

class StatusDatabaseUpdateThread(BasicThread):
    """
    These threads will send the update requests to all the virtual machine servers
    periodically.
    """
    def __init__(self, updateHandler, sleepTime):
        """
        Initializes the thread's state
        Args:
            updateHandler: the object that will send the update request packets.
            sleepTime: the number of seconds that will separate two consecutive
            update requests.
        """
        BasicThread.__init__(self, "Status database update thread")
        self.__handler = updateHandler
        self.__sleepTime = sleepTime
        
    def run(self):
        """
        Sends the update request packets when necessary.
        Args:
            None
        Returns:
            Nothing
        """
        while not self.finish() :
            self.__handler.sendUpdateRequestPackets()
            sleep(self.__sleepTime)
        


