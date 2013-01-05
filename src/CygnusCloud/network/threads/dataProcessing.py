'''
Created on Jan 5, 2013

@author: luis
'''
from utils.threads import QueueProcessingThread

class _IncomingDataThread(QueueProcessingThread):
    """
    A class associated with the incoming packages threads.
    This threads will process the incoming packages.
    """
    def __init__(self, queue, callbackObject):
        QueueProcessingThread.__init__(self, queue)   
        self.__callbackObject = callbackObject     
        
    def processElement(self, e):
        self.__callbackObject.processPacket(e)
        
class _OutgoingDataThread(QueueProcessingThread):
    def processElement(self, e):
        (connection, packet) = e
        connection.sendPacket(packet)