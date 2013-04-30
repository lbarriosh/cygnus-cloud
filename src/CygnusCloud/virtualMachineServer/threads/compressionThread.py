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
    def __init__(self, imageDirectory, transferDirectory, queue):
        QueueProcessingThread.__init__(self, "File compression thread", queue)
        self.__workingDirectory = imageDirectory
        self.__transferDirectory = transferDirectory
        
    def processElement(self, data):
        # Extraemos el fichero en el directorio de trabajo
        compressor = ZipBasedCompressor(path.join(self.__transferDirectory, str(data["SourceImageID"]) + ".zip"), "r")
        compressor.extract(path.join(self.__workingDirectory, str(data["SourceImageID"])))
        # Movemos el fichero de definicion
        #Buscamos el fichero con extension .xml en la ruta de descompresión
        for files in listdir(path.join(self.__workingDirectory, str(data["SourceImageID"]))):
            if files.endswith(".xml"):
                defFile = files
                break
        #movemos el fichero al directorio
        shutil.move(defFile, data["configFilePath"])
        
        #Cambiamos los permisos del resto de archivos
        ChildProcessManager.runCommandInForeground("sudo su", Exception)
        for files in listdir(path.join(self.__workingDirectory, str(data["SourceImageID"]))):
            ChildProcessManager.runCommandInForeground("chmod 666 " + files, Exception)
        ChildProcessManager.runCommandInForeground("exit", Exception)
         
        # Arrancamos la máquina virtual
        
        # TODO: informar de errores cuando no se pueda descomprimir el fichero
