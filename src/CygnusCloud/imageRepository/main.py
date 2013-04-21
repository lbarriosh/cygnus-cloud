# -*- coding: utf8 -*-
'''
Created on Apr 21, 2013

@author: luis
'''

import sys
from constants import ImageRepositoryConstantsManager
from database.utils.configuration import DBConfigurator
from imageRepository import ImageRepository
from time import sleep

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
    
    imageRepository = ImageRepository(cm.getConstant('workingDirectory'))
    imageRepository.connectToDatabases("ImageRepositoryDB", cm.getConstant("dbUser"), cm.getConstant("dbUserPassword"))
    imageRepository.startListenning(cm.getConstant("certificatePath"), cm.getConstant("commandsPort"), 
                                    cm.getConstant("dataPort"), cm.getConstant('maxUploadSlots'), cm.getConstant('maxDownloadSlots'))
    while (not imageRepository.hasFinished()) :
        sleep(1)
    imageRepository.stopListenning()
    
