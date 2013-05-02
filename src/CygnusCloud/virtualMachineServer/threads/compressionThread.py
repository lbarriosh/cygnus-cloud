# -*- coding: utf8 -*-
'''
Created on Apr 28, 2013

@author: luis
'''

from ccutils.threads import QueueProcessingThread
from ccutils.compression.zipBasedCompressor import ZipBasedCompressor
from virtualMachineServer.exceptions.vmServerException import VMServerException
from os import path
from os import listdir
from os import makedirs
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
        
        if(data["Retrieve"]):
            # Extraemos el fichero en el directorio de trabajo
            extractFilePath = path.join(self.__workingDirectory, str(data["SourceImageID"]))
            compressor = ZipBasedCompressor(path.join(self.__transferDirectory, str(data["SourceImageID"]) + ".zip"), "r")
            compressor.extract(extractFilePath)
            # TODO: informar de errores cuando no se pueda descomprimir el fichero
            #Cambiamos los permisos de los ficheros y buscamos el xml
            definitionFilePath = path.join(self.__configFilePath,str(data["SourceImageID"]))
            #Creamos el directorio de definicion en el caso de que no exista
            if not path.exists(definitionFilePath):
                makedirs(definitionFilePath)
        
            for files in listdir(extractFilePath):
                ChildProcessManager.runCommandInForegroundAsRoot("chmod 666 " + path.join(extractFilePath,files), Exception)
                if files.endswith(".xml"):
                    #movemos el fichero al directorio
                    definitionFile = files
                    shutil.move(path.join(extractFilePath,definitionFile), definitionFilePath)

            #Registramos la máquina virtual
            self.__dbConnector.createImage(data["SourceImageID"],path.join(str(data["SourceImageID"]),"OS.qcow2"),
                                           path.join(str(data["SourceImageID"]),"Data.qcow2"),
                                           path.join(str(data["SourceImageID"]),definitionFile),False)

         
            # Arrancamos la máquina virtual
            self.__domainHandler.createDomain(data["SourceImageID"], data["UserID"], data["CommandID"])
            #TODO:Añadir información del repositorio a el diccionario
        else:
        
            #Añadimos los ficheros a un zip
            extractFilePath = path.join(self.__workingDirectory, str(data["SourceImageID"]))
            compressor = ZipBasedCompressor(path.join(self.__transferDirectory, str(data["SourceImageID"]) + ".zip"), "r")
            compressor.addFile(data["DataPath"], data["DataPath"])
            compressor.addFile(data["OSPath"], data["OSPath"])
            compressor.addFile(data["DefinitionPath"], data["DefinitionPath"])
            #Borramos los ficheros
            ChildProcessManager.runCommandInForeground("rm " + data["DataPath"], VMServerException)
            ChildProcessManager.runCommandInForeground("rm " + data["OSPath"], VMServerException)
            dataDirectory = path.dirname(data["DataPath"])
            osDirectory = path.dirname(data["OSPath"])
            if (listdir(dataDirectory) == []) :
                ChildProcessManager.runCommandInForeground("rm -rf " + dataDirectory, VMServerException)
            if (osDirectory != dataDirectory and listdir(osDirectory) == []) :
                ChildProcessManager.runCommandInForeground("rm -rf " + osDirectory, VMServerException)
            #TODO:Encolar la nueva peticion a la cola de transferencias    
            
