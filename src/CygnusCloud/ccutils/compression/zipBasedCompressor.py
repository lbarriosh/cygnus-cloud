# -*- coding: utf8 -*-
'''
Created on Apr 28, 2013

@author: luis
'''

from ccutils.processes.childProcessManager import ChildProcessManager
from os import path

class ZipBasedCompressor():
    
    def createCompressedFile(self, filePath, fileNameList):
        '''
        Añade un archivo al fichero comprimido
        Args:
            filename: nombre del archivo a comprimir
            filenameInCompressedFile: nombre del archivo en el archivo comprimido
        '''
        args = filePath + " "
        for fileName in fileNameList :
            args += fileName + " "
        try :
            ChildProcessManager.runCommandInForeground("zip -j " + args, Exception)
        except Exception as e:
            if ("Nothing to do" in e.message) :
                pass
            else :
                raise e

    def extractFile(self, path, outputDirectory):
        '''
        Extrae los archivos del fichero comprimido en una ruta
        Args:
            path: Ruta en la que descomprimir el fichero
        '''
        if (outputDirectory == None) :
            outputDirectory = path.dirname(path)
        ChildProcessManager.runCommandInForeground("unzip " + path + " -d " + outputDirectory, Exception)