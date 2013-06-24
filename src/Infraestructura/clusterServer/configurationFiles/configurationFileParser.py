# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: configurationFileParser.py    
    Version: 3.0
    Description: cluster server configuration file parser
    
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

class ClusterServerConfigurationFileParser(ConfigurationFileParser):
    """
    Cluster server configuration file parser
    """    
    def __init__(self):
        """
        Initializes the parser's state
        Args:
            None
        """
        ConfigurationFileParser.__init__(self)
        
    def _getExpectedSections(self):
        return ['Database configuration', 'Network configuration', 'Load balancer configuration', 'Other settings', 'Image repository connection data']
    
    def _readConfigurationParameters(self):
        keys = ['mysqlRootsPassword', 'dbUser', 'dbUserPassword']
        for key in keys:
            self._readString('Database configuration', key)        
        
        self._readBoolean('Network configuration', 'useSSL')
        self._readString('Network configuration', 'certificatePath')
        self._readInt('Network configuration', 'listenningPort')
        
        self._readString('Load balancer configuration', 'loadBalancingAlgorithm')
        keys = ['vCPUsWeight', 'vCPUsExcessThreshold', 'ramWeight', 'storageSpaceWeight', 'temporarySpaceWeight']
        for key in keys:
            self._readFloat('Load balancer configuration', key)
            
        keys = ['vmBootTimeout', 'statusUpdateInterval']
        for key in keys:
            self._readFloat('Other settings', key)
        self._readFloat('Other settings', 'averageCompressionRatio')
        
        self._readString('Image repository connection data', 'imageRepositoryIP')
        self._readInt('Image repository connection data', 'imageRepositoryPort')