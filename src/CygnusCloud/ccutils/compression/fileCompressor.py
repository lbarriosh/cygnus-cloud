'''
Created on 27/04/2013

@author: saguma
'''

class FileCompressor():
    
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