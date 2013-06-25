# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: main.py    
    Version: 5.0
    Description: cluster endpoint daemon entry point
    
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

import sys
from clusterEndpoint.configurationFiles.configurationFileParser import ClusterEndpointConfigurationFileParser
from clusterEndpoint.entryPoint.clusterEndpointEntryPoint import ClusterEndpointEntryPoint

if __name__ == "__main__" :
    if (len(sys.argv) != 2) :
        print "A configuration file path is needed"
        sys.exit()
    try :
        parser = ClusterEndpointConfigurationFileParser()
        parser.parseConfigurationFile(sys.argv[1])
    except Exception as e:
        print e.message
        sys.exit()
        
    endpoint = ClusterEndpointEntryPoint()
    
    endpoint.connectToDatabases(parser.getConfigurationParameter("mysqlRootsPassword"), "ClusterEndpointDB", 
                                "CommandsDB", "./databases/ClusterEndpointDB.sql", 
                                "./databases/CommandsDB.sql", parser.getConfigurationParameter("websiteUser"), 
                                parser.getConfigurationParameter("websiteUserPassword"),  parser.getConfigurationParameter("endpointUser"), 
                                parser.getConfigurationParameter("endpointUserPassword"), parser.getConfigurationParameter("minCommandInterval"))
    try :
        endpoint.connectToClusterServer(parser.getConfigurationParameter('useSSL'),
                                        parser.getConfigurationParameter("certificatePath"), parser.getConfigurationParameter("clusterServerIP"), 
                                        parser.getConfigurationParameter("clusterServerListenningPort"), parser.getConfigurationParameter("statusDBUpdateInterval"),
                                        parser.getConfigurationParameter("commandTimeout"), parser.getConfigurationParameter("commandTimeoutCheckInterval"))
        endpoint.processCommands()
        endpoint.disconnectFromClusterServer()
    except Exception as e:
        endpoint.doEmergencyStop()
        print "Error: " + e.message