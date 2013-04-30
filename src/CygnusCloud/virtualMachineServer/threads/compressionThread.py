# -*- coding: utf8 -*-
'''
Created on Apr 28, 2013

@author: luis
'''

from ccutils.threads import QueueProcessingThread
from ccutils.compression.zipBasedCompressor import ZipBasedCompressor
from os import path
from os import listdir
import shutil
from ccutils.processes.childProcessManager import ChildProcessManager

class CompressionThread(QueueProcessingThread):
    def __init__(self, imageDirectory, transferDirectory, queue,configFilePath,dbConnector,domainHandler):
        QueueProcessingThread.__init__(self, "File compression thread", queue)
        self.__workingDirectory = imageDirectory
        self.__transferDirectory = transferDirectory
        self.__configFilePath = configFilePath
        self.__dbConnector = dbConnector
        self.__domainHandler = domainHandler
        
    def processElement(self, data):
        # Extraemos el fichero en el directorio de trabajo
        extractFilePath = path.join(self.__workingDirectory, str(data["SourceImageID"]))
        compressor = ZipBasedCompressor(path.join(self.__transferDirectory, str(data["SourceImageID"]) + ".zip"), "r")
        compressor.extract(extractFilePath)
        # TODO: informar de errores cuando no se pueda descomprimir el fichero
        #Cambiamos los permisos de los ficheros y buscamos el xml
        definitionFilePath = path.join(self.__configFilePath,str(data["SourceImageID"]))
        for files in listdir(extractFilePath):
            ChildProcessManager.runCommandInForegroundAsRoot("chmod 666 " + path.join(extractFilePath,files), Exception)
            if files.endswith(".xml"):
                #movemos el fichero al directorio
                definitionFile = files
                shutil.move(path.join(extractFilePath,definitionFile), definitionFilePath)

        #Registramos la máquina virtual
        self.__dbConnector.createImage(data["SourceImageID"],path.join(extractFilePath,"OS.qcow2"),
                                       path.join(extractFilePath,"Data.qcow2"),
                                       path.join(definitionFilePath,definitionFile),False)

         
        # Arrancamos la máquina virtual
        self.__domainHandler.createDomain(data["SourceImageID"],data["UserID"],data["DomainID"])
        
