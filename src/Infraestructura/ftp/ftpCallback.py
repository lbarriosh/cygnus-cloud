# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: configurableFTPServer.py    
    Version: 3.0
    Description: configurable FTP server definitions
    
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
  
class FTPCallback(object):   
    """
    This class defines the interface common to all the FTP server callbacks.
    """ 
       
    def on_disconnect(self):
        """
        Handles a client abrupt disconnection
        Args:
            None
        Returns:
            Nothing
        """
        raise NotImplementedError
    
    def on_login(self, username):
        """
        Handles a client login
        Args:
            username: the client's username
        Returns:
            Nothing
        """
        raise NotImplementedError    
    
    def on_logout(self, username):
        """
        Handles a client logout
        Args:
            username: the client's username
        Returns:
            Nothing
        """
        raise NotImplementedError    
    
    def on_file_sent(self, f):
        """
        Handles a file sent event
        Args:
            f: a filename
        Returns:
            Nothing
        """
        raise NotImplementedError    
    
    def on_file_received(self, f):
        """
        Handles a file received event
        Args:
            f: a filename
        Returns:
            Nothing
        """
        raise NotImplementedError    
    
    def on_incomplete_file_sent(self, f):
        """
        Handles a file partially sent event
        Args:
            f: a filename
        Returns:
            Nothing
        """
        raise NotImplementedError    
    
    def on_incomplete_file_received(self, f):
        """
        Handles a file partially received event
        Args:
            f: a filename
        Returns:
            Nothing
        """
        raise NotImplementedError