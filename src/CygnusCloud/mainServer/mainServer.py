# -*- coding: utf8 -*-
'''
Main server entry point
@author: Luis Barrios Hernández
@version: 1.0
'''

from reactor import MainServerReactor
from time import sleep

rootsPassword = ""
dbUser ="cygnuscloud"
dbPassword ="cygnuscloud"
scriptPath = "../database/MainServerDB.sql"
databaseName = "MainServerDB"
certificatePath ="/home/luis/Certificates"
listeningPort = 9000

if __name__ == "__main__":
    reactor = MainServerReactor()
    reactor.connectToDatabase(rootsPassword, dbUser, dbPassword, scriptPath, databaseName)
    reactor.startListenning(certificatePath, 9000)
    while not reactor.hasFinished() :
        sleep(30)