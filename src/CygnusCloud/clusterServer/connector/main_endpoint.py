# -*- coding: utf8 -*
'''
Created on Apr 3, 2013

@author: luis
'''

import sys
from constants import WebServerEndpointConstantsManager
from webServerEndpoint import WebServerEndpoint
from endpointException import EndpointException

if __name__ == "__main__" :
    # Parsear el fichero de configuración
    if (len(sys.argv) != 2) :
        print "A configuration file path is needed"
        sys.exit()
    try :
        cm = WebServerEndpointConstantsManager()
        cm.parseConfigurationFile(sys.argv[1])
    except Exception as e:
        print "Error: " + e.message
        sys.exit()
        
    endpoint = WebServerEndpoint()
    
    endpoint.connectToDatabases(cm.getConstant("mysqlRootsPassword"), cm.getConstant("statusDBName"), 
                                cm.getConstant("commandsDBName"), cm.getConstant("statusdbSQLFilePath"), 
                                cm.getConstant("commandsdbSQLFilePath"), cm.getConstant("websiteUser"), 
                                cm.getConstant("websiteUserPassword"),  cm.getConstant("endpointUser"), 
                                cm.getConstant("endpointUserPassword"))
    try :
        endpoint.connectToClusterServer(cm.getConstant("certificatePath"), cm.getConstant("clusterServerIP"), 
                                        cm.getConstant("clusterServerListenningPort"), cm.getConstant("statusDBUpdateInterval"))
        endpoint.processCommands()
        endpoint.disconnectFromClusterServer()
    except EndpointException as e:
        endpoint.closeDBConnections()
        print "Error: " + e.message