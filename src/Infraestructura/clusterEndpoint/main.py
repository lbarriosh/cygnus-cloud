# -*- coding: utf8 -*
'''
Created on Apr 3, 2013

@author: luis
'''

import sys
from clusterEndpoint.configurationFiles.configurationFileParser import ClusterEndpointConfigurationFileParser
from clusterEndpoint.entryPoint.clusterEndpointEntryPoint import ClusterEndpointEntryPoint

if __name__ == "__main__" :
    # Parsear el fichero de configuración
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
        endpoint.connectToClusterServer(parser.getConfigurationParameter("certificatePath"), parser.getConfigurationParameter("clusterServerIP"), 
                                        parser.getConfigurationParameter("clusterServerListenningPort"), parser.getConfigurationParameter("statusDBUpdateInterval"),
                                        parser.getConfigurationParameter("commandTimeout"), parser.getConfigurationParameter("commandTimeoutCheckInterval"))
        endpoint.processCommands()
        endpoint.disconnectFromClusterServer()
    except Exception as e:
        endpoint.doEmergencyStop()
        print "Error: " + e.message