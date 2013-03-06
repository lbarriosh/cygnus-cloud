'''
Created on 06/03/2013

@author: luis
'''
from threading import BoundedSemaphore
class ConnectionStatus(object):
    """
    A class that stores a connection's status and allows its modification
    in a thread-safe manner.
    """
    def __init__(self, status):
        """
        Initializes the status using its argument.
        """
        self._status = status
        self.__semaphore = BoundedSemaphore(1)
    def get(self):
        """
        Returns the status value
        """
        return self._status
    def set(self, value):
        """
        Modifies the status.
        """
        with self.__semaphore :
            self._status = value
