# -*- coding: utf8 -*-
'''
Main server entry point
@author: Luis Barrios Hernández
@version: 1.0
'''

from clusterServer.reactor.clusterServerReactor import ClusterServerReactor
from time import sleep

rootsPassword = ""
dbName = "ClusterServerDB"
dbUser ="cygnuscloud"
dbPassword ="cygnuscloud"
scriptPath = "../database/ClusterServerDB.sql"
databaseName = "ClusterServerDB"
certificatePath ="/home/luis/Certificates"
listeningPort = 9000

if __name__ == "__main__":
    reactor = ClusterServerReactor()
    reactor.connectToDatabase(rootsPassword, dbName, dbUser, dbPassword, scriptPath)
    reactor.startListenning(certificatePath, 9000)
    while not reactor.hasFinished() :
        sleep(10)
    reactor.shutdown()
