# -*- coding: utf8 -*-
'''
Punto de entrada del servidor de máquinas virtuales

@author: Luis Barrios Hernández
@version: 2.0
'''

from ccutils.databases.configuration import DBConfigurator
from reactor.vmServerReactor import VMServerReactor
from time import sleep
from ccutils.passwords.rootPasswordHandler import RootPasswordHandler
from constants import VMServerConstantsManager
from ccutils.processes.childProcessManager import ChildProcessManager
import sys

if __name__ == "__main__" :
    # Parsear el fichero de configuración
    if (len(sys.argv) != 2) :
        print "A configuration file path is needed"
        sys.exit()
    try :
        parser = VMServerConstantsManager()
        parser.parseConfigurationFile(sys.argv[1])
    except Exception as e:
        print "Error: " + e.message
        sys.exit()
        
    # Pedir la contraseña de root. Es necesaria para poder cambiar los permisos
    password_ok = False
    while (not password_ok) :        
        try :            
            ChildProcessManager.runCommandInForegroundAsRoot("ls", Exception)
            password_ok = True
        except Exception:
            print "Wrong password. Please, key it in again."
            RootPasswordHandler().clear()
        
    # Crear la base de datos (si es necesario)
    configurator = DBConfigurator(parser.getConstant("mysqlRootsPassword"))
    configurator.runSQLScript(parser.getConstant("databaseName"), "./database/VMServerDB.sql")
    # Crear un usuario y darle permisos
    configurator.addUser(parser.getConstant("databaseUserName"), parser.getConstant("databasePassword"), parser.getConstant("databaseName"), True)
    # Crear el servidor de máquinas virtuales
    vmServer = VMServerReactor(parser)    
    # Dormir hasta que se apague
    while not vmServer.has_finished():
        sleep(10) 
    vmServer.shutdown()       
    