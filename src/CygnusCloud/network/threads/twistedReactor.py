# -*- coding: utf8 -*-
'''
Twisted reactor thread definitions.
@author: Luis Barrios Hernández
@version: 1.5
'''

from twisted.internet import reactor
from threading import Thread

class _TwistedReactorThread(Thread):
    """
    These threads run the twisted reactor loop.
    @attention: Once the reactor is stopped, it won\'t be able to start again.
    """
    def __init__(self):
        """
        Initializes the thread's state.
        Args:
            None
        Returns:
            Nothing
        """
        Thread.__init__(self, name="Twisted reactor thread")
        
    def __workaround(self):
        """
        This is a workaround to fix a nasty Twisted bug. 
        Args:
            None
        Returns:
            Nothing
        """
        reactor.callLater(1, self.__workaround)
    
    def run(self):        
        """
        Starts and runs the twisted reactor loop.
        Args:
            None
        Returns:
            Nothing
        """
        reactor.callLater(1, self.__workaround)
        reactor.run(installSignalHandlers=0)
        
    def stop(self):
        """
        Stops the twisted reactor loop
        Args:
            None
        Returns:
            Nothing
        """
        reactor.stop()  