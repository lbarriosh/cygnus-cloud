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
    __instance = None
    def __init__(self):
        
        self.__password = None
        
    @staticmethod
    def getInstance():
        if (RootPasswordHandler.__instance == None) :
            RootPasswordHandler.__instance = RootPasswordHandler()
        return RootPasswordHandler.__instance
            
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

if __name__ == "__main__" :
    password = RootPasswordHandler.getInstance().getRootsPassword()
    print password
            

        