# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: main.py    
    Version: 5.0
    Description: virtual machine server entry point
    
    Copyright 2012-13 Luis Barrios Hernández, Adrián Fernández Hernández,
        Samuel Guayerbas Martín

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
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
    if (len(sys.argv) != 2) :
        print "A configuration file path is needed"
        sys.exit()
    try :
        parser = VMServerConfigurationFileParser()
        parser.parseConfigurationFile(sys.argv[1])
    except Exception as e:
        print e.message
        sys.exit()
        
    # Read root's password. It's vital to change the downloaded files' permissions.
    password_ok = False
    while (not password_ok) :        
        try :            
            ChildProcessManager.runCommandInForegroundAsRoot("ls", Exception)
            password_ok = True
        except Exception:
            print "Wrong password. Please, key it in again."
            RootPasswordHandler().clear()
        
    # Configure the database
    rootPassword = parser.getConfigurationParameter("mysqlRootsPassword")
    configurator = DBConfigurator(rootPassword)
    configurator.runSQLScript("VMServerDB", "./database/VMServerDB.sql", "root", rootPassword) 
    configurator.addUser(parser.getConfigurationParameter("databaseUserName"), parser.getConfigurationParameter("databasePassword"), "VMServerDB", True)
    
    # Create the directories (if necessary)
    parameters = ["configFilePath", "sourceImagePath", "executionImagePath", "TransferDirectory"]
    for param in parameters :
        param_path = parser.getConfigurationParameter(param)
        if (not os.path.exists(param_path)):
            os.mkdir(param_path)
    
    # Finish the initialization process
    vmServer = VMServerReactor(parser)  
    while not vmServer.has_finished():
        sleep(10) 
    vmServer.shutdown()       
    