# -*- coding: utf8 -*-
'''
Basic thread class definitions.
@author: Luis Barrios Hernández
@version: 1.2
'''

from ccutils.threads.basicThread import BasicThread

class QueueProcessingThread(BasicThread):
    """
    A class associated with a data processing thread.
    These threads read data from a queue and process
    them in an abstract way.
    """
    def __init__(self, threadName, compressionQueue):
        """
        Initializes the thread's state
        Args:
            compressionQueue: the compressionQueue to monitor.
        """
        BasicThread.__init__(self, threadName)        
        self._queue = compressionQueue   
        
    def processElement(self, element):
        """
        Processes an element
        Args:
            element: the element to process
        Returns:
            Nothing
        """
        raise NotImplementedError
    
    def run(self):
        """
        Processes the queue until it's empty and the thread is finish.
        """        
        while not (self.finish() and self._queue.isEmpty()):
            while not self._queue.isEmpty() :
                element = self._queue.dequeue()
                self.processElement(element)                
            sleep(0.01) # Sleep for 10 milliseconds when there's nothing to do   