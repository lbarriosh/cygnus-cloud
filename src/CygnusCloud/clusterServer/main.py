# -*- coding: utf8 -*-
'''
Main server entry point
@author: Luis Barrios Hernández
@version: 1.0
'''

from clusterServer.reactor.clusterServerReactor import ClusterServerReactor
import sys
from constants import ClusterServerConstantsManager

if __name__ == "__main__":
    # Parsear el fichero de configuración
    if (len(sys.argv) != 2) :
        print "A configuration file path is needed"
        sys.exit()
    try :
        cm = ClusterServerConstantsManager()
        cm.parseConfigurationFile(sys.argv[1])
    except Exception as e:
        print "Error: " + e.message
        sys.exit()
    reactor = ClusterServerReactor(cm.getConstant("vmBootTimeout"))
    reactor.connectToDatabase(cm.getConstant("mysqlRootsPassword"), "ClusterServerDB", 
                              cm.getConstant("dbUser"), cm.getConstant("dbPassword"), cm.getConstant("scriptPath"))
    reactor.startListenning("../../Certificates", cm.getConstant("listenningPort"))
    reactor.monitorVMBootCommands()
    reactor.closeNetworkConnections()
