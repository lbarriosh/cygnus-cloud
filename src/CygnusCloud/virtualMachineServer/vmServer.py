# -*- coding: utf8 -*-
'''
Punto de entrada del servidor de máquinas virtuales

@author: luis
'''

from database.utils.configuration import DBConfigurator
from vmClient import VMClient
from time import sleep
from constantes import databaseName, databaseUserName, databasePassword, mysqlRootsPassword


if __name__ == "__main__" :
    # Crear la base de datos (si es necesario)
    configurator = DBConfigurator(mysqlRootsPassword)
    configurator.runSQLScript("../database/VMServerDB.sql")
    # Crear un usuario y darle permisos
    configurator.addUser(databaseUserName, databasePassword, databaseName, True)
    # Crear el servidor de máquinas virtuales
    vmServer = VMClient()
    # Dormir hasta que se apague
    while not vmServer.hasFinished():
        sleep(20)