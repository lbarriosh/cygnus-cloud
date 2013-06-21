# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: ftpClient.py    
    Version: 1.3
    Description: FTP client definitions
    
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
from ftplib import FTP
import os

class FTPClient(object):
    """
    This class provides methods to interact with Python's FTP client
    at a higher abstraction level.
    """    
    def __init__(self):
        """
        Initializes the client's state
        Args:
            None
        """
        self.__ftp = FTP()

    
    def connect(self, host, port, timeout, user, password):
        """"
        Establishes a connection with a FTP server
        Args:
            host: the FTP server's IPv4 address
            port: the FTP server's listenning port
            timeout: connection timeout (in seconds)
            user: an username
            password: a password
        """
        self.__ftp.connect(host, port, timeout)
        self.__ftp.login(user, password)
        self.__ftp.set_pasv(True)        
    
    def storeFile(self, fileName, localDirectory, serverDirectory=None):
        """
        Stores a file in the FTP server
        Args:
            fileName: a file name (NOT a path)
            localDirectory: a local directory, where the file to upload is located.
            serverDirectory: a server directory. If it's None, the file will be uploaded
                to the server's root directory
        Returns:
            Nothing
        """
        if (serverDirectory != None) :
            self.__ftp.cwd(serverDirectory)        
        self.__ftp.storbinary("STOR " + fileName, open(os.path.join(localDirectory, fileName), "rb"))        
    
    def retrieveFile(self, fileName, localDirectory, serverDirectory=None):
        """
        Downloads a file from the FTP server
        Args:
            fileName: a file name (NOT a path)
            localDirectory: a local directory, where the downloaded file will be located.
            serverDirectory: a server directory. If it's None, the file will be uploaded
                to the server's root directory
        Returns:
            Nothing
        """
        if (serverDirectory != None) :
            self.__ftp.cwd(serverDirectory)
        with open(os.path.join(localDirectory, fileName), "wb") as f:
            def ftpCallback(data):
                f.write(data)
            self.__ftp.retrbinary("RETR " + fileName, ftpCallback)        
    
    def disconnect(self):
        """
        Closes the connection with the FTP server
        Args:
            None
        Returns:
            Nothing
        """
        self.__ftp.quit()