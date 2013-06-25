# -*- coding: UTF8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: dataProcessing.py    
    Version: 1.5
    Description: data processing threads definitions
    
    Copyright 2012-13 Luis Barrios Hernández, Adrián Fernández Hernández,
        Samuel Guayerbas Martín
        
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''
from ccutils.threads.queueProcessingThread import QueueProcessingThread
from ccutils.dataStructures.multithreadingCounter import MultithreadingCounter

class IncomingDataThread(QueueProcessingThread):
    """
    This threads will process the incoming network packets.
    """
    def __init__(self, transferQueue, callbackObject):
        """
        Initializes the thread's state
        Args:
            transferQueue: The incoming packages transferQueue 
            callbackObject: The callback object that will process
            all the received packets.
        """
        QueueProcessingThread.__init__(self, "Incoming data processing thread", transferQueue)   
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
    """
    These threads will sent the outgoing packets.
    """
    
    def __init__(self, transferQueue):
        """
        Initializes the thread's state.
        Args:
        """
        QueueProcessingThread.__init__(self, "Outgoing data processing thread", transferQueue)
        
    
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