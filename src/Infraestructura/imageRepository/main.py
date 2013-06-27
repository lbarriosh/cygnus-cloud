# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: main.py    
    Version: 3.0
    Description: image repository entry point
    
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
import sys
import os
from imageRepository.configurationFiles.configurationFileParser import ImageRepositoryConfigurationFileParser
from ccutils.databases.configuration import DBConfigurator
from imageRepository.reactor.imageRepositoryReactor import ImageRepositoryReactor

if __name__ == "__main__" :
    
    if (len(sys.argv) != 2) :
        print "A configuration file path is needed"
        sys.exit()
    try :
        parser = ImageRepositoryConfigurationFileParser()
        parser.parseConfigurationFile(sys.argv[1])
    except Exception as e:
        print e.message
        sys.exit()
    
    rootPassword= parser.getConfigurationParameter('mysqlRootsPassword')
    dbConfigurator = DBConfigurator(rootPassword)
    dbConfigurator.runSQLScript("ImageRepositoryDB", "./database/ImageRepositoryDB.sql", "root", rootPassword)
    dbConfigurator.addUser(parser.getConfigurationParameter('dbUser'), parser.getConfigurationParameter('dbUserPassword'), "ImageRepositoryDB")
    
    if (not os.path.exists(parser.getConfigurationParameter('FTPRootDirectory'))):
        os.mkdir(parser.getConfigurationParameter('FTPRootDirectory'))
        
    imageRepository = ImageRepositoryReactor(parser.getConfigurationParameter('FTPRootDirectory'))
    imageRepository.connectToDatabase("ImageRepositoryDB", parser.getConfigurationParameter("dbUser"), parser.getConfigurationParameter("dbUserPassword"))
    
    imageRepository.startListenning(parser.getConfigurationParameter("FTPListenningInterface"), parser.getConfigurationParameter("useSSL"),
                                    parser.getConfigurationParameter("certificatePath"), parser.getConfigurationParameter("commandsPort"), 
                                    parser.getConfigurationParameter("FTPPort"), parser.getConfigurationParameter('maxConnections'), parser.getConfigurationParameter('maxConnectionsPerIP'),
                                    parser.getConfigurationParameter("uploadBandwidthRatio"), parser.getConfigurationParameter("downloadBandwidthRatio"), parser.getConfigurationParameter("FTPUserName"),
                                    parser.getConfigurationParameter("FTPPasswordLength"))
        
    imageRepository.initTransfers() # The main thread will dispatch all the transfers.
    imageRepository.stopListenning()   
