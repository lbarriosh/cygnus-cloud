# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: configurationFileParser.py    
    Version: 3.0
    Description: Virtual machine server configuration file parser
    
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

from ccutils.configurationFiles.configurationFileParser import ConfigurationFileParser

class VMServerConfigurationFileParser(ConfigurationFileParser):
    """
    Virtual machine server configuration file parser
    """    
    def __init__(self):
        """
        Initializes the parser's state
        Args:
            None
        """
        ConfigurationFileParser.__init__(self)
        
    def _getExpectedSections(self):
        return ['Database configuration', 'Virtual Network Configuration', 'VNC server configuration', 
                'FTP Client Configuration', 'Network configuration', 'Paths']
    
    def _readConfigurationParameters(self):
        keys = ['mysqlRootsPassword', 'databaseUserName', 'databasePassword']
        for key in keys:
            self._readString('Database configuration', key)
            
        self._readBoolean('Virtual Network Configuration', 'createVirtualNetworkAsRoot')
        keys = ['vnName', 'gatewayIP', 'netMask', 'dhcpStartIP', 'dhcpEndIP']
        for key in keys:
            self._readString('Virtual Network Configuration', key)
        
        keys = ['vncNetworkInterface', 'passwordLength', 'websockifyPath']
        for key in keys:
            self._readString('VNC server configuration', key)
        self._readBoolean('VNC server configuration', 'useQEMUWebsockets')
        
        self._readBoolean('Network configuration', 'useSSL')
        self._readString('Network configuration', 'certificatePath')
        self._readInt('Network configuration', 'listenningPort')
        
        keys = ['FTPTimeout', 'MaxTransferAttempts']
        for key in keys:
            self._readInt('FTP Client Configuration', key)
        
        keys = ['configFilePath', 'sourceImagePath', 'executionImagePath', 'TransferDirectory']
        for key in keys:
            self._readString('Paths', key)