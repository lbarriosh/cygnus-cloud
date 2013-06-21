# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: ccFTPHandler.py    
    Version: 1.5
    Description: FTP handler definitions
    
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

from pyftpdlib.handlers import FTPHandler
from os import remove

class CygnusCloudFTPHandler(FTPHandler):
    """
    These objects handle the events triggered by the pyftpdlib FTP server.
    """    
    
    def on_disconnect(self):
        """
        Handles a client abrupt disconnection
        Args:
            None
        Returns:
            Nothing
        """
        if (CygnusCloudFTPHandler.ftpCallback != None) :
            CygnusCloudFTPHandler.ftpCallback.on_disconnect()
    
    def on_login(self, username):
        """
        Handles a client login
        Args:
            username: the client's username
        Returns:
            Nothing
        """
        if (CygnusCloudFTPHandler.ftpCallback != None) :
            CygnusCloudFTPHandler.ftpCallback.on_login(username)
    
    def on_logout(self, username):
        """
        Handles a client logout
        Args:
            username: the client's username
        Returns:
            Nothing
        """
        if (CygnusCloudFTPHandler.ftpCallback != None):
            CygnusCloudFTPHandler.ftpCallback.on_logout(username)
    
    def on_file_sent(self, f):
        """
        Handles a file sent event
        Args:
            f: a filename
        Returns:
            Nothing
        """
        if (CygnusCloudFTPHandler.ftpCallback != None) :
            CygnusCloudFTPHandler.ftpCallback.on_file_sent(f)
    
    def on_file_received(self, f):
        """
        Handles a file received event
        Args:
            f: a filename
        Returns:
            Nothing
        """
        if (CygnusCloudFTPHandler.ftpCallback != None):
            CygnusCloudFTPHandler.ftpCallback.on_file_received(f)
    
    def on_incomplete_file_sent(self, f):
        """
        Handles a file partially sent event
        Args:
            f: a filename
        Returns:
            Nothing
        """
        if (CygnusCloudFTPHandler.ftpCallback != None):
            CygnusCloudFTPHandler.ftpCallback.on_incomplete_file_sent(f)
    
    def on_incomplete_file_received(self, f):
        """
        Handles a file partially received event
        Args:
            f: a filename
        Returns:
            Nothing
        """
        if (CygnusCloudFTPHandler.ftpCallback != None) :
            CygnusCloudFTPHandler.ftpCallback.on_incomplete_file_received(f)
        else :
            remove(f)        