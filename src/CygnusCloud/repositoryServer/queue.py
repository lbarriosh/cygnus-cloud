
from ccutils.threads import QueueProcessingThread
from time import sleep

class WaitQueue(QueueProcessingThread):
        
    def __init__(self, queue, hasSlot, sendFreeSlot):
        """
        hasSlot: función a la que preguntar si hay hueco para atender la peticion
        sendFreeSlot: función que enviará el paquete para avisar de que hay un hueco para atender la peticion
        """
        QueueProcessingThread.__init__(self, "TransferWaitQueue", queue)
        self.__hasSlot = hasSlot
        self.__sendFreeSlot = sendFreeSlot
    def processElement(self, element):
        while (not self.__hasSlot()) :
            sleep(1)
            
        self.__sendFreeSlot(element["IP"], element["requestID"])
        

        