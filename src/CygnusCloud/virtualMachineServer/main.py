# -*- coding: utf8 -*-
'''
Punto de entrada del servidor de máquinas virtuales

@author: Luis Barrios Hernández
@version: 1.0
'''

from database.utils.configuration import DBConfigurator
from vmServer import VMServer
from time import sleep
from constants import VMServerConstantsManager
import sys

if __name__ == "__main__" :
    # Parsear el fichero de configuración
    if (len(sys.argv) != 2) :
        print "A configuration file path is needed"
        sys.exit()
    try :
        cm = VMServerConstantsManager()
        cm.parseConfigurationFile(sys.argv[1])
    except Exception as e:
        print "Error: " + e.message
        sys.exit()
        
    # Crear la base de datos (si es necesario)
    configurator = DBConfigurator(cm.getConstant("mysqlRootsPassword"))
    configurator.runSQLScript("VMServerDB", "../database/VMServerDB.sql")
    # Crear un usuario y darle permisos
    configurator.addUser(cm.getConstant("databaseUserName"), cm.getConstant("databasePassword"), "VMServerDB", True)
    # Crear el servidor de máquinas virtuales
    vmServer = VMServer(cm)    
    # Dormir hasta que se apague
    while not vmServer.halt():
        sleep(10) 
    vmServer.shutdown()       
    