# -*- coding: utf8 -*-
'''
Created on Apr 28, 2013

@author: luis
'''

import zipfile
from ccutils.compression.fileCompressor import FileCompressor

class ZipBasedCompressor(FileCompressor):
    
    def __init__(self, filename, mode):
        self.__zip = zipfile.ZipFile(filename, mode, zipfile.ZIP_DEFLATED, True)
        pass
    
    def addFile(self, filename, filenameInCompressedFile=None):
        '''
        Añade un archivo al fichero comprimido
        Args:
            filename: nombre del archivo a comprimir
            filenameInCompressedFile: nombre del archivo en el archivo comprimido
        '''
        self.__zip.write(filename, filenameInCompressedFile)
    
    def extract(self, path):
        '''
        Extrae los archivos del fichero comprimido en una ruta
        Args:
            path: Ruta en la que descomprimir el fichero
        '''
        self.__zip.extractall(path)