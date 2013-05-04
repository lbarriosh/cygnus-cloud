# -*- coding: utf8 -*-
'''
A module that stores and handles root's password on runtime.
@author: Luis Barrios Hernández
@version: 1.0
'''

from getpass import getpass

class RootPasswordHandler(object):
    """
    A class that stores and returns root's password on runtime
    """
    _instance = None    
        
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RootPasswordHandler, cls).__new__(
                                cls, *args, **kwargs)
            cls._instance.clear()
        return cls._instance   
            
    def getRootsPassword(self):
        """
        Returns root's password, asking for it when necessary.
        Args: 
            None
        Returns:
            A string containing root's password.
        """
        if (self.__password == None) :
            self.__password = getpass("Root's password: ")
        return self.__password
    
    def clear(self):
        self.__password = None

if __name__ == "__main__" :
    password = RootPasswordHandler.getInstance().getRootsPassword()
    print password
            

        