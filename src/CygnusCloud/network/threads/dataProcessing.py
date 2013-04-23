# -*- coding: utf8 -*-
'''
Data processing threads definitions.
@author: Luis Barrios Hernández
@version: 1.1
'''
from ccutils.threads import QueueProcessingThread
from ccutils.dataStructures.multithreadingCounter import MultithreadingCounter

class IncomingDataThread(QueueProcessingThread):
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
        QueueProcessingThread.__init__(self, "Incoming data processing thread", queue)   
        self.__callbackObject = callbackObject     
        self.__referenceCounter = MultithreadingCounter()
        
    def start(self):
        """
        Starts the thread
        Args:
            None
        Returns:
            Nothing
        """
        self.__referenceCounter.increment()
        if (self.__referenceCounter.read() == 1) :
            QueueProcessingThread.start(self)
        
    def stop(self, join):
        """
        Asks this thread to terminate.
        Args:
            join: When True, the calling thread will wait the incoming data thread
            to terminate. When False, the calling thread will only ask this thread to terminate.
        Returns: 
            Nothing
        """
        self.__referenceCounter.decrement()
        if self.__referenceCounter.read() == 0 :
            QueueProcessingThread.stop(self)
            if join :
                self.join()
                
    def run(self):
        QueueProcessingThread.run(self)
        
    def processElement(self, e):
        """
        Processes a received packet
        Args:
            e: The packet to process
        Returns:
            Nothing
        """
        self.__callbackObject.processPacket(e)
        
class OutgoingDataThread(QueueProcessingThread):
    
    def __init__(self, queue):
        QueueProcessingThread.__init__(self, "Outgoing data processing thread", queue)
        
    """
    Outgoing packages thread class.
    """
    def processElement(self, e):
        """
        Processes an (connection, packet to send) pair.
        Args:
            e: The pair to process. Its packet will be sent through its connection.
        Returns:
            Nothing
        """
        (connection, packet, client_ip, client_port) = e
        connection.sendPacket(packet, client_ip, client_port)