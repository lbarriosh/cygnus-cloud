'''
Created on 27/04/2013

@author: saguma
'''
from ccutils.threads import QueueProcessingThread
from network.ftp.ftpClient import FTPClient


class RepositoryComunicationThread(QueueProcessingThread):
    
    def __init__(self, queue, compressManager):
        '''
        Crea una hilo que procesará la compresión/descompresion de las imágenes 
        Args:
            queue: Cola en la que se añadirán los archivos a procesar
            compressManager: Clase que controla los archivos comprimidos
        '''
        QueueProcessingThread.__init__(self, "Compress thread", queue)
        self.__compressManager = compressManager
        self.__ftp = FTPClient()
    
    def processElement(self, data):
        """
        Comprime o descomprime las imagenes necesarias
        Args:
            data: es un diccionario que tiene las siguientes claves
                - compress: booleano que dice si hay que comprimir una imagen (True) o comprimirlo (False)
                - ftpIP: la dirección IP del servidor FTP
                - ftpPort: el puerto de escucha del servidor FTP
                - ftpUser: nombre de usuario del servidor FTP
                - ftpPassword: la contraseña del servidor FTP
                - filename: lista de archivos a descargar/subir
                - outputPath: ruta donde descomprimir el archivo (compress = False)
                              crear del archivo comprimido (compress = True)
        Returns:
            Nothing
        """
        
        if (data["compress"]) :
            # Creo el archivo comprimido y añado todos los archivos
            compressFile = self.__compressManager(data["outputPath"], "w")
            for (inputFile, compressName) in data["inputFiles"] :
                compressFile.addFile(inputFile, compressName)
            # Envio el archivo creado por FTP
            self.__ftp.connect(data["ftpIP"], data["ftpPort"], self.__cManager.getConstant("ftpTimeout"), data["ftpUser"], data["ftpPassword"])
            self.__ftp.storeFile(data["filename"], data["outputPath"])
            self.__ftp.disconnect()
            # TODO: Borrar el archivo creado
        else :
            # Me conecto al servidor FTP para bajarme el archivo
            self.__ftp.connect(data["ftpIP"], data["ftpPort"], self.__cManager.getConstant("ftpTimeout"), data["ftpUser"], data["ftpPassword"])
            self.__ftp.retrieveFile(data["filename"], data["outputPath"])
            self.__ftp.disconnect()
            # Descomprimo el archivo
            compressFile = self.__compressManager(data["filename"], "r")
            compressFile.extract(data["outputPath"])
            # TODO: Borrar el archivo bajado
            
                
        