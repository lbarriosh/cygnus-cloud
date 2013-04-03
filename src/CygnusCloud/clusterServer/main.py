# -*- coding: utf8 -*-
'''
Main server entry point
@author: Luis Barrios Hernández
@version: 1.0
'''

from clusterServer.reactor.clusterServerReactor import ClusterServerReactor

mysqlRootsPassword = ""
dbName = "ClusterServerDB"
dbUser ="cygnuscloud"
dbPassword ="cygnuscloud"
scriptPath = "../database/ClusterServerDB.sql"
databaseName = "ClusterServerDB"
certificatePath ="/home/luis/Certificates"
listeningPort = 9000
vmBootTimeout = 10

if __name__ == "__main__":
    reactor = ClusterServerReactor(vmBootTimeout)
    reactor.connectToDatabase(mysqlRootsPassword, dbName, dbUser, dbPassword, scriptPath)
    reactor.startListenning(certificatePath, 9000)
    reactor.monitorVMBootCommands()
    reactor.shutdown()
