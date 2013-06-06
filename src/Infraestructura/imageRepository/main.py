# -*- coding: utf8 -*-
'''
Punto de entrada del repositorio de imágenes

@author: luis
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
    
    dbConfigurator = DBConfigurator(parser.getConfigurationParameter('mysqlRootsPassword'))
    dbConfigurator.runSQLScript("ImageRepositoryDB", "./database/ImageRepositoryDB.sql")
    dbConfigurator.addUser(parser.getConfigurationParameter('dbUser'), parser.getConfigurationParameter('dbUserPassword'), "ImageRepositoryDB")
    
    imageRepository = ImageRepositoryReactor(parser.getConfigurationParameter('FTPRootDirectory'))
    imageRepository.connectToDatabase("ImageRepositoryDB", parser.getConfigurationParameter("dbUser"), parser.getConfigurationParameter("dbUserPassword"))
    
    imageRepository.startListenning(parser.getConfigurationParameter("FTPListenningInterface"), parser.getConfigurationParameter("useSSL"),
                                    parser.getConfigurationParameter("certificatePath"), parser.getConfigurationParameter("commandsPort"), 
                                    parser.getConfigurationParameter("FTPPort"), parser.getConfigurationParameter('maxConnections'), parser.getConfigurationParameter('maxConnectionsPerIP'),
                                    parser.getConfigurationParameter("uploadBandwidthRatio"), parser.getConfigurationParameter("downloadBandwidthRatio"), parser.getConfigurationParameter("FTPUserName"),
                                    parser.getConfigurationParameter("FTPPasswordLength"))
    
    if (not os.path.exists(parser.getConfigurationParameter('FTPRootDirectory'))):
        os.mkdir(parser.getConfigurationParameter('FTPRootDirectory'))
        
    imageRepository.initTransfers() # Aprovechamos el hilo principal para inicializar las transferencias
    imageRepository.stopListenning() # Es imprescindible hacer esto en el hilo principal para que no se cuelgue
    
