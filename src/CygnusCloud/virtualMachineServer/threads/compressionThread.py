# -*- coding: utf8 -*-
'''
Created on Apr 28, 2013

@author: luis
'''

from ccutils.threads import QueueProcessingThread
from ccutils.compression.zipBasedCompressor import ZipBasedCompressor
from virtualMachineServer.exceptions.vmServerException import VMServerException
from os import path, listdir, makedirs
import shutil
from ccutils.processes.childProcessManager import ChildProcessManager
from virtualMachineServer.reactor.transfer_t import TRANSFER_T

class CompressionThread(QueueProcessingThread):
    def __init__(self, imageDirectory, transferDirectory, compressionQueue, transferQueue, configFilePath, dbConnector, domainHandler, editedImagesData):
        QueueProcessingThread.__init__(self, "File compression thread", compressionQueue)
        self.__imageDirectory = imageDirectory
        self.__transferDirectory = transferDirectory
        self.__definitionFileDirectory = configFilePath
        self.__dbConnector = dbConnector
        self.__domainHandler = domainHandler
        self.__editedImagesData = editedImagesData
        self.__transferQueue = transferQueue
        self.__compressor = ZipBasedCompressor()

        
    def processElement(self, data):
        
        if(data["Transfer_Type"] == TRANSFER_T.CREATE_IMAGE):
            
            # Extraemos el fichero en el directorio que alberga las imágenes
            imageDirectory = path.join(self.__imageDirectory, str(data["TargetImageID"]))
            compressedFilePath = path.join(self.__transferDirectory, str(data["SourceImageID"]) + ".zip")
            self.__compressor.extractFile(compressedFilePath, imageDirectory)
            
            # Borramos el fichero .zip
            ChildProcessManager.runCommandInForeground("rm " + compressedFilePath, VMServerException)
            
            # Cambiamos los permisos de los ficheros y buscamos el fichero de definición
            definitionFileDirectory = path.join(self.__definitionFileDirectory, str(data["TargetImageID"]))            
            
            # Creamos el directorio de definicion en el caso de que no exista
            if not path.exists(definitionFileDirectory):
                makedirs(definitionFileDirectory)
        
            for fileName in listdir(imageDirectory):
                ChildProcessManager.runCommandInForegroundAsRoot("chmod 666 " + path.join(imageDirectory, fileName), VMServerException)
                if fileName.endswith(".xml"):
                    # movemos el fichero al directorio
                    definitionFile = fileName
                    shutil.move(path.join(imageDirectory, fileName), definitionFileDirectory)
                    

            # Registramos la máquina virtual
            self.__dbConnector.createImage(data["TargetImageID"], path.join(str(data["TargetImageID"]), "OS.qcow2"),
                                           path.join(str(data["TargetImageID"]), "Data.qcow2"),
                                           path.join(str(data["TargetImageID"]), definitionFile), False)
         
            # Arrancamos la máquina virtual
            self.__domainHandler.createDomain(data["TargetImageID"], data["UserID"], data["CommandID"])
            
            # Guardamos los datos de conexión al repositorio            
            self.__editedImagesData[data["CommandID"]] = {"RepositoryIP": data["RepositoryIP"], "RepositoryPort" : data["RepositoryPort"]}
        else:        
            # Comprimimos los ficheros
            
            zipFilePath = path.join(self.__transferDirectory, str(data["TargetImageID"]) + ".zip")
            
            self.__compressor.createCompressedFile(zipFilePath, [data["OSImagePath"], data["DataImagePath"], data["DefinitionFilePath"]])
            
            # Borramos los ficheros fuente
            ChildProcessManager.runCommandInForeground("rm -rf " + path.dirname(data["DefinitionFilePath"]), Exception)
            ChildProcessManager.runCommandInForeground("rm -rf " + path.dirname(data["OSImagePath"]), Exception)
            
            # Encolamos la petición
            
            data.pop("DataImagePath")
            data.pop("OSImagePath")
            data.pop("DefinitionFilePath")
           
            data["SourceFilePath"] = path.basename(zipFilePath)            
           
            self.__transferQueue.queue(data)