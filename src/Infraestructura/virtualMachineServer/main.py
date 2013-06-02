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
from virtualMachineServer.configurationFiles.configurationFileParser import VMServerConfigurationFileParser
from ccutils.processes.childProcessManager import ChildProcessManager
import sys
import os

if __name__ == "__main__" :
    # Parsear el fichero de configuración
    if (len(sys.argv) != 2) :
        print "A configuration file path is needed"
        sys.exit()
    try :
        parser = VMServerConfigurationFileParser()
        parser.parseConfigurationFile(sys.argv[1])
    except Exception as e:
        print e.message
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
    configurator = DBConfigurator(parser.getConfigurationParameter("mysqlRootsPassword"))
    configurator.runSQLScript("VMServerDB", "./database/VMServerDB.sql")
    # Crear un usuario y darle permisos
    configurator.addUser(parser.getConfigurationParameter("databaseUserName"), parser.getConfigurationParameter("databasePassword"), "VMServerDB", True)
    
    # Crear los directorios
    parameters = ["configFilePath", "sourceImagePath", "executionImagePath", "TransferDirectory"]
    for param in parameters :
        param_path = parser.getConfigurationParameter(param)
        if (not os.path.exists(param_path)):
            os.mkdir(param_path)
    
    # Terminar con la inicialización
    vmServer = VMServerReactor(parser)    
    # Dormir hasta que se apague
    while not vmServer.has_finished():
        sleep(10) 
    vmServer.shutdown()       
    