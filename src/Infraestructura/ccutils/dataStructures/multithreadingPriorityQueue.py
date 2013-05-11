# -*- coding: utf8 -*-
'''
A module that contains the thread-safe priority queue definitions
@author: Luis Barrios Hernández
@version 1.0
'''

from threading import BoundedSemaphore
from threading import Thread

class GenericThreadSafePriorityQueueException(Exception):
    pass

class GenericThreadSafePriorityQueue(object):
    """
    A priority queue with multi-threading support.
    @attention: This objects are NOT iterable to avoid nasty iterator issues.    
    """
    def __init__(self):
        """
        Creates an empty priority transferQueue
        Args:
            None
        Returns:
            Nothing
        """
        # We use this to speed up the transferQueue operations
        self._data = dict()
        # We use a semaphore to avoid compilation problems in Python 3.x
        self.__semaphore = BoundedSemaphore(1) 
        self.__elements = 0
        
    def queue(self, priority, data):
        """
        Adds a new element to the queue
        Args:
            priority: an integer priority value.
            data: the data to add to the queue
        Returns:
            Nothing
        Raises:
            GenericThreadSafePriorityQueueException: this exceptions will be raised when
            the priority is not an integer value.
        """
        # Check arguments
        if not isinstance(priority, int) :
            raise GenericThreadSafePriorityQueueException("The priority must be an integer value")
        # Acquire semaphore, add data
        with self.__semaphore:
            if not self._data.has_key(priority) :
                self._data[priority] = []       
            self._data[priority].append(data)
            self.__elements += 1
            
    def dequeue(self):
        """
        Pops an element from the queue.
        Args:
            None
        Returns:
            The popped element.
        Raises:
            GenericThreadSafePriorityQueueException: this exceptions will be raised when the queue is empty.
        """
        with self.__semaphore:
            if self.__elements == 0:
                raise GenericThreadSafePriorityQueueException("The queue is empty")
            keys = self._data.keys()
            keys.sort() # This is the little price to pay for an efficient queue operation. If the number of keys 
                        # remains constant, this operation has an O(1) time complexity.
            self.__elements -= 1
            for key in keys:
                if not len(self._data[key]) == 0 :
                    return self._data[key].pop(0)
    
    def isEmpty(self):
        """
        Checks if the list es empty or not
        Args:
            None
        Returns:
            True if the queue is empty and false otherwise.
        """
        with self.__semaphore:
            return self.__elements == 0
        
if __name__ == "__main__" :
    
    class DumbThread(Thread):
        def __init__(self, transferQueue, thid, threshold):
            Thread.__init__(self)
            self.__queue = transferQueue
            self.__thid = thid
            self.__threshold = threshold
    
        def run(self):
            print 'Dumb thread ' + str(self.__thid) + " is running now\n"
            priority = range(-self.__threshold, self.__threshold)
            for item in priority :
                self.__queue.queue(item, "Dumb thread " + str(self.__thid) + " " + str(item))
            
        
    # Create an empty queue
    q = GenericThreadSafePriorityQueue()
    # Add some stuff to it in three separate threads
    dumb1 = DumbThread(q, 1, 2)
    dumb2 = DumbThread(q, 2, 4)
    dumb3 = DumbThread(q, 3, 6)
    dumb1.start()
    dumb2.start()
    dumb3.start()
    dumb1.join()
    dumb2.join()
    dumb3.join()
    print "Queue content:"
    # Print all the data stored into the queue
    while not q.isEmpty():
        print q.dequeue()
    
    
        
    
        
