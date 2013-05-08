'''
Created on Apr 28, 2013

@author: luis
'''
from ccutils.dataStructures.multithreadingList import GenericThreadSafeList

class GenericThreadSafeQueue(object):
    
    def __init__(self):
        self.__list = GenericThreadSafeList()
        
    def queue(self, element):
        self.__list.append(element)
        
    def isEmpty(self):
        return self.__list.isEmpty()
        
    def dequeue(self):
        return self.__list.pop(0)