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

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.servers import FTPServer
from pyftpdlib.handlers import ThrottledDTPHandler
from network.interfaces.ipAddresses import get_ip_address
from ccutils.processes.childProcessManager import ChildProcessManager
from re import sub  
from ftp.pyftpdlibInteraction.ccFTPHandler import CygnusCloudFTPHandler
from ftp.pyftpdlibInteraction.ftpServerThread import FTPServerThread

class ConfigurableFTPServer(object):
    """
    This class provides methods to interact with the pyftpdlib FTP server
    at a higher abstraction level.
    """    
    
    def __init__(self, banner):
        """
        Initializes the server's state
        Args:
            banner: the banner that will be shown when users log in.
        """
        self.__authorizer = DummyAuthorizer()       
        self.__banner = banner 
        self.__thread = None        
    
    def startListenning(self, networkInterface, port, maxConnections, maxConnectionsPerIP, ftpCallback = None,
                        downloadBandwidthRatio=0.8, uploadBandwitdhRatio=0.8):
        """
        Starts the FTP server
        Args:
            networkInterface: the network interface that will be used to perform the FTP transfers
            port: a listenning port
            maxConnections: maximum connection number
            maxConnectionsPerIP: maximum connection number per IP address
            ftpCallback: the callback that will handle the events. If it's none, almost nothing will be
                done to handle them.
            downloadBandwidthRatio: maximum download bandwidth fraction
            uploadBandwidthRatio: maximum upload bandwidth fraction
        Returns:
            Nothing
        """
        ip_address = get_ip_address(networkInterface)
        handler = CygnusCloudFTPHandler
        handler.ftpCallback = ftpCallback
        handler.authorizer = self.__authorizer
        handler.banner = self.__banner  
        link_bandwidth = ChildProcessManager.runCommandInForeground("/sbin/ethtool eth0 | grep -i Speed | cut -b 9-", Exception)
        if ("Mb/s" in link_bandwidth) :
            power = 1024 ** 2
        else :
            power = 1024 ** 3
        link_bandwidth = int(sub('[^0-9]', '', link_bandwidth))
        dtp_handler = ThrottledDTPHandler
        dtp_handler.read_limit = link_bandwidth * downloadBandwidthRatio * power
        dtp_handler.write_limit = link_bandwidth * uploadBandwitdhRatio * power 
        handler.dtp_handler = dtp_handler
        address = (ip_address, port)
        self.__ftpServer = FTPServer(address, handler)
        self.__ftpServer.max_cons = maxConnections
        self.__ftpServer.max_cons_per_ip = maxConnectionsPerIP
        self.__thread = FTPServerThread(self.__ftpServer)
        self.__thread.start()        
    
    def addUser(self, username, password, homedir, permissions):
        """
        Registers a new user
        Args:
            username: an username
            password: a password
            homedir: a home directory
            permissions: this string sets the new user's permissions.
                Read permissions:
                    - "e" = change directory (CWD command)
                    - "l" = list filess (LIST, NLST, STAT, MLSD, MLST, SIZE, MDTM commands)
                    - "r" = retrieve files from the server (RETR command)
                   
                   Write permissions:
                    - "a" = append data to an existing f (APPE command)
                    - "d" = delete file or directory (DELE, RMD commands)
                    - "f" = rename file or directory (RNFR, RNTO commands)
                    - "m" = create directory (MKD command)
                    - "w" = store a file to the server (STOR, STOU commands)
                    - "M" = change file mode (SITE CHMOD command)
        Returns:
            Nothing
        """
        self.__authorizer.add_user(username, password, homedir, permissions)        
    
    def removeUser(self, username):
        """
        Deletes an user
        Args:
            username: an username
        Returns:
            Nothing
        """
        self.__authorizer.remove_user(username)        
    
    def stopListenning(self):
        """
        Stops the FTP servers
        Args:
            None
        Returns:
            Nothing
        """
        if (self.__thread == None) :
            raise Exception("The FTP server is not running")
        self.__thread.stop()