# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: ftpServerCallback.py    
    Version: 2.0
    Description: FTP events callback
    
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

from ftp.ftpCallback import FTPCallback
from os import remove, path
from ccutils.processes.childProcessManager import ChildProcessManager

class FTPServerCallback(FTPCallback):
    """
    FTP events callback
    """   
    def __init__(self, slotCounter, dbConnector):
        """
        Initializes the callback's state
        Args:
            slotCounter: the slot counter
            dbConnector: the image repository database connector
        """
        self.__slotCounter = slotCounter
        self.__dbConnector = dbConnector

    def on_disconnect(self):
        """
        Handles a client abrupt disconnection
        Args:
            None
        Returns:
            Nothing
        """
        self.__slotCounter.increment()

    def on_login(self, username):
        """
        Handles a client login
        Args:
            username: the client's username
        Returns:
            Nothing
        """
        pass

    def on_logout(self, username):
        """
        Handles a client logout
        Args:
            username: the client's username
        Returns:
            Nothing
        """
        pass

    def on_file_sent(self, f):
        """
        Handles a file sent event
        Args:
            f: a filename
        Returns:
            Nothing
        """
        pass
    
    def on_file_received(self, f):
        """
        Handles a file received event
        Args:
            f: a filename
        Returns:
            Nothing
        """
        self.__dbConnector.handleFinishedUploadTransfer(f)
    
    def on_incomplete_file_sent(self, f):
        """
        Handles a file partially sent event
        Args:
            f: a filename
        Returns:
            Nothing
        """
        self.__dbConnector.handlePartialDownloadTransfer(f)

    def on_incomplete_f_received(self, f):    
        """
        Handles a file partially received event
        Args:
            f: a filename
        Returns:
            Nothing
        """
        remove(f)
        ChildProcessManager.runCommandInForeground("rm -rf " + path.dirname(f), Exception)