'''
Created on 27/04/2013

@author: saguma
'''

import zipfile

class CompressFile():
    
    def __init__(self, filename, mode):
        pass
    
    def addFile(self, filename, filenameInCompressFile=None):
        '''
        Añade un archivo al fichero comprimido
        Args:
            filename: nombre del archivo a comprimir
            filenameInCompressFile: nombre del archivo en el archivo comprimido
        '''
        raise NotImplementedError
    
    def extract(self, path):
        '''
        Extrae los archivos del fichero comprimido en una ruta
        Args:
            path: Ruta en la que descomprimir el fichero
        '''
        raise NotImplementedError
    
class ZipFile(CompressFile):
    
    def __init__(self, filename, mode):
        self.__zip = zipfile.ZipFile(filename, mode, zipfile.ZIP_DEFLATED, True)
        pass
    
    def addFile(self, filename, filenameInCompressFile=None):
        '''
        Añade un archivo al fichero comprimido
        Args:
            filename: nombre del archivo a comprimir
            filenameInCompressFile: nombre del archivo en el archivo comprimido
        '''
        self.__zip.write(filename, filenameInCompressFile)
    
    def extract(self, path):
        '''
        Extrae los archivos del fichero comprimido en una ruta
        Args:
            path: Ruta en la que descomprimir el fichero
        '''
        self.__zip.extractall(path)
    
    