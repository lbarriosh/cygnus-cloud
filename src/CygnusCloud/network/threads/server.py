# -*- coding: utf8 -*-
'''
Server connection thread definitions.
@author: Luis Barrios Hernández
@version: 2.5
'''

from utils.threads import BasicThread
from time import sleep
        
class _ServerWaitThread(BasicThread):
    """
    These threads will monitor a new server connection and will update it
    when it's ready to be used.
    """    
    def __init__(self, factory, registerMethod, startThreadMethod):
        """
        Initializes the thread's state
        Args:
            factory: The protocol factory that will build the connection's protocol.
            registerMethod: the method to register the new active connection.
            startThreadMethod: the method to start the new connection's incoming package
            thread.
        """
        BasicThread.__init__(self)        
        self.__factory = factory
        self.__registerMethod = registerMethod
        self.__startThreadMethod = startThreadMethod
        
    def run(self): 
        """
        Checks if the connection is ready. If so, finishes its initialization and terminates.
        Args:
            None
        Returns:
            Nothing
        """
        while not self.stopped() and self.__factory.getInstance() == None :
            sleep(0.01)
        if not self.stopped() :
            self.__registerMethod(self.__factory.getInstance())
            self.__startThreadMethod() 