# -*- coding: utf8 -*-
'''
Created on Apr 28, 2013

@author: luis
'''

from ccutils.threads import QueueProcessingThread
from ccutils.compression.zipBasedCompressor import ZipBasedCompressor
from os import path

class CompressionThread(QueueProcessingThread):
    def __init__(self, imageDirectory, transferDirectory, queue):
        QueueProcessingThread.__init__(self, "File compression thread", queue)
        self.__workingDirectory = imageDirectory
        self.__transferDirectory = transferDirectory
        
    def processElement(self, data):
        # Extraemos el fichero en el directorio de trabajo
        compressor = ZipBasedCompressor(path.join(self.__transferDirectory, str(data["SourceImageID"]) + ".zip"), "r")
        compressor.extract(path.join(self.__workingDirectory, str(data["SourceImageID"])))
        # Arrancamos la máquina virtual
        
        # TODO: informar de errores cuando no se pueda descomprimir el fichero
