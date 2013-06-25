# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: main.py    
    Version: 5.0
    Description: cluster server entry point
    
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

from clusterServer.mainReactor.clusterServerMainReactor import ClusterServerMainReactor
import sys
from clusterServer.configurationFiles.configurationFileParser import ClusterServerConfigurationFileParser

if __name__ == "__main__":
    if (len(sys.argv) != 2) :
        print "A configuration file path is needed"
        sys.exit()
    try :
        parser = ClusterServerConfigurationFileParser()
        parser.parseConfigurationFile(sys.argv[1])
    except Exception as e:
        print e.message
        sys.exit()
    loadBalancerSettings = [parser.getConfigurationParameter("loadBalancingAlgorithm"), 
                            parser.getConfigurationParameter("vCPUsWeight"), parser.getConfigurationParameter("vCPUsExcessThreshold"),
                            parser.getConfigurationParameter("ramWeight"), parser.getConfigurationParameter("storageSpaceWeight"),
                            parser.getConfigurationParameter("temporarySpaceWeight")]
    reactor = ClusterServerMainReactor(loadBalancerSettings, parser.getConfigurationParameter("averageCompressionRatio"),
                                   parser.getConfigurationParameter("vmBootTimeout"))
    reactor.connectToDatabase(parser.getConfigurationParameter("mysqlRootsPassword"), "ClusterServerDB", 
                              parser.getConfigurationParameter("dbUser"), parser.getConfigurationParameter("dbUserPassword"), 
                              "./database/ClusterServerDB.sql")
    reactor.startListenning(parser.getConfigurationParameter("useSSL"), parser.getConfigurationParameter("certificatePath"), parser.getConfigurationParameter("listenningPort"), 
                            parser.getConfigurationParameter("imageRepositoryIP"), parser.getConfigurationParameter("imageRepositoryPort"), 
                            parser.getConfigurationParameter("statusUpdateInterval"))
    reactor.monitorVMBootCommands()
    reactor.closeNetworkConnections()