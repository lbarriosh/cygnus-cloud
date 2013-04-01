# -*- coding: utf8 -*-
'''
Punto de entrada del servidor de máquinas virtuales

@author: Luis Barrios Hernández
@version: 1.0
'''

from database.utils.configuration import DBConfigurator
from vmServer import VMServer
from time import sleep
from constantes import databaseName, databaseUserName, databasePassword, mysqlRootsPassword


if __name__ == "__main__" :
    # Crear la base de datos (si es necesario)
    configurator = DBConfigurator(mysqlRootsPassword)
    configurator.runSQLScript(databaseName, "../database/VMServerDB.sql")
    # Crear un usuario y darle permisos
    configurator.addUser(databaseUserName, databasePassword, databaseName, True)
    # Crear el servidor de máquinas virtuales
    vmServer = VMServer()
    # Dormir hasta que se apague
    while not vmServer.hasFinished():
        sleep(10)        
    vmServer.closeNetworkConnections()