# -*- coding: utf8 -*-
'''
Data processing threads definitions.
@author: Luis Barrios Hernández
@version: 1.0
'''
from utils.threads import QueueProcessingThread
from utils.multithreadingCounter import MultithreadingCounter

class _IncomingDataThread(QueueProcessingThread):
    """
    Incoming packages thread class.
    This threads will process the incoming packages.
    """
    def __init__(self, queue, callbackObject):
        """
        Initializes the thread's state
        Args:
            queue: The incoming packages queue 
            callbackObject: The callback object that will process
            all the received packets.
        """
        QueueProcessingThread.__init__(self, queue)   
        self.__callbackObject = callbackObject     
        self.__referenceCounter = MultithreadingCounter()
        
    def start(self):
        self.__referenceCounter.increment()
        QueueProcessingThread.start(self)
        
    def stop(self, join):
        self.__referenceCounter.decrement()
        if self.__referenceCounter.read() == 0 :
            QueueProcessingThread.stop(self)
            if join :
                self.join()
        
    def processElement(self, e):
        self.__callbackObject.processPacket(e)
        
class _OutgoingDataThread(QueueProcessingThread):
    """
    Outgoing packages thread class.
    """
    def processElement(self, e):
        (connection, packet) = e
        connection.sendPacket(packet)