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
    @attention: This queues ARE NOT ITERABLE. I've done this ON PURPOSE, just to ensure that
    no threads will monopolize the synchronization mechanism.
    
    """
    def __init__(self):
        """
        Creates an empty priority queue
        """
        # We use this to speed up the queue operations
        self.__data = dict()
        # We use a semaphore to avoid compilation problems in Python 3.x
        self.__semaphore = BoundedSemaphore(1) 
        self.__elements = 0
        
    def queue(self, priority, data):
        # Check arguments
        if not isinstance(priority, int) :
            raise GenericThreadSafePriorityQueueException("The priority must be an integer value")
        # Acquire semaphore, add data
        with self.__semaphore:
            if not self.__data.has_key(priority) :
                self.__data[priority] = []       
            self.__data[priority].append(data)
            self.__elements += 1
            
    def dequeue(self):
        with self.__semaphore:
            if self.__elements == 0:
                raise GenericThreadSafePriorityQueueException("The queue is empty")
            keys = self.__data.keys()
            keys.sort() # This is the little price to pay for an efficient queue operation. If the number of keys 
                        # remains constant, this operation has an O(1) time complexity.
            self.__elements -= 1
            for key in keys:
                if not len(self.__data[key]) == 0 :
                    return self.__data[key].pop(0)
    
    def isEmpty(self):
        """
        Checks if the list es empty or not
        """
        with self.__semaphore:
            return self.__elements == 0
        
if __name__ == "__main__" :
    
    class DumbThread(Thread):
        def __init__(self, queue, thid, threshold):
            Thread.__init__(self)
            self.__queue = queue
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
    
    
        
    
        
