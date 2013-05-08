# -*- coding: utf8 -*-
'''
Punto de entrada del repositorio de imágenes

@author: luis
'''

import sys
from constants import ImageRepositoryConstantsManager
from database.utils.configuration import DBConfigurator
from imageRepository import ImageRepository

if __name__ == "__main__" :
    
    if (len(sys.argv) != 2) :
        print "A configuration file path is needed"
        sys.exit()
    try :
        cm = ImageRepositoryConstantsManager()
        cm.parseConfigurationFile(sys.argv[1])
    except Exception as e:
        print "Error: " + e.message
        sys.exit()
    
    dbConfigurator = DBConfigurator(cm.getConstant('mysqlRootsPassword'))
    dbConfigurator.runSQLScript("ImageRepositoryDB", cm.getConstant('scriptPath'))
    dbConfigurator.addUser(cm.getConstant('dbUser'), cm.getConstant('dbUserPassword'), "ImageRepositoryDB")
    
    imageRepository = ImageRepository(cm.getConstant('FTPRootDirectory'))
    imageRepository.connectToDatabase("ImageRepositoryDB", cm.getConstant("dbUser"), cm.getConstant("dbUserPassword"))
    
    imageRepository.startListenning(cm.getConstant("FTPListenningInterface"), cm.getConstant("certificatePath"), cm.getConstant("commandsPort"), 
                                    cm.getConstant("FTPPort"), cm.getConstant('maxConnections'), cm.getConstant('maxConnectionsPerIP'),
                                    cm.getConstant("uploadBandwidthRatio"), cm.getConstant("downloadBandwidthRatio"), cm.getConstant("FTPUserName"),
                                    cm.getConstant("FTPPasswordLength"))
    imageRepository.initTransfers() # Aprovechamos el hilo principal para inicializar las transferencias
    imageRepository.stopListenning() # Es imprescindible hacer esto en el hilo principal para que no se cuelgue
    
