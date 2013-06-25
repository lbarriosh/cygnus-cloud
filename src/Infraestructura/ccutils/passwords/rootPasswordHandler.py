# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: rootPasswordHandler.py    
    Version: 2.0
    Description: roots password handler definitions
    
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

from getpass import getpass

class RootPasswordHandler(object):
    """
    A class that reads, stores and returns root's password on runtime
    """
    _instance = None    
        
    def __new__(cls, *args, **kwargs):
        # Dirty singleton hack.
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
        """
        Deletes the stored password
        Args:
            None
        Returns:
            Nothing
        """
        self.__password = None