# -*- coding: utf8 -*-
'''
Main server entry point
@author: Luis Barrios Hernández
@version: 1.0
'''

from clusterServer.mainReactor.clusterServerMainReactor import ClusterServerMainReactor
import sys
from clusterServer.configurationFiles.configurationFileParser import ClusterServerConfigurationFileParser

if __name__ == "__main__":
    # Parsear el fichero de configuración
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
