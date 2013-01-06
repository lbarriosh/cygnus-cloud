# -*- coding: utf8 -*-
'''
Data processing threads definitions.
@author: Luis Barrios Hernández
@version: 1.0
'''
from utils.threads import QueueProcessingThread

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
        
    def processElement(self, e):
        self.__callbackObject.processPacket(e)
        
class _OutgoingDataThread(QueueProcessingThread):
    """
    Outgoing packages thread class.
    """
    def processElement(self, e):
        (connection, packet) = e
        connection.sendPacket(packet)