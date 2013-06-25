# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: configurationFileParser.py    
    Version: 4.0
    Description: image repository configuration file parser
    
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

class ImageRepositoryConfigurationFileParser(ConfigurationFileParser):
    """
    Image repository configuration file parser
    """    
    def __init__(self):
        """
        Initializes the parser's state
        Args:
            None
        """
        ConfigurationFileParser.__init__(self)
        
    def _getExpectedSections(self):
        return ['Database configuration', 'Network configuration', 'FTP Server configuration']
    
    def _readConfigurationParameters(self):
        keys = ['mysqlRootsPassword', 'dbUser', 'dbUserPassword']
        for key in keys:
            self._readString('Database configuration', key)
            
        self._readString('Network configuration', 'certificatePath')
        self._readInt('Network configuration', 'commandsPort')
        self._readBoolean('Network configuration', 'useSSL')
        
        keys = ['FTPListenningInterface', 'FTPRootDirectory', 'FTPUserName']
        for key in keys:
            self._readString('FTP Server configuration', key)
        
        keys = ['FTPPort', 'maxConnections', 'maxConnectionsPerIP', 'FTPPasswordLength']
        for key in keys:
            self._readInt('FTP Server configuration', key)
            
        keys = ['uploadBandwidthRatio', 'downloadBandwidthRatio']
        for key in keys:
            self._readFloat('FTP Server configuration', key)