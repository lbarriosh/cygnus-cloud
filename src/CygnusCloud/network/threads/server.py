# -*- coding: utf8 -*-
'''
Created on Jan 4, 2013

@author: luis
'''


from utils.threads import BasicThread
from time import sleep           

        
class _ServerWaitThread(BasicThread):
    
    def __init__(self, factory, registerMethod, startThreadMethod):
        BasicThread.__init__(self)        
        self.__factory = factory
        self.__registerMethod = registerMethod
        self.__startThreadMethod = startThreadMethod
        
    def run(self): 
        while not self.stopped() and self.__factory.getInstance() == None :
            sleep(0.01)
        if not self.stopped() :
            self.__registerMethod(self.__factory.getInstance())
            self.__startThreadMethod() 