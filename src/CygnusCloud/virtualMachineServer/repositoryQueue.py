'''
Created on 27/04/2013

@author: saguma
'''
from ccutils.threads import QueueProcessingThread
from network.ftp.ftpClient import FTPClient
import os
    
class RepositoryComunicationCallback():
    def downloadedImage(self):
        raise NotImplementedError

    def uploadedImage(self):
        raise NotImplementedError

class RepositoryComunicationThread(QueueProcessingThread):
    
    def __init__(self, queue, compressManager, callback = None):
        '''
        Crea una hilo que procesará la compresión/descompresion de las imágenes 
        Args:
            queue: Cola en la que se añadirán los archivos a procesar
            compressManager: Clase que controla los archivos comprimidos
        '''
        QueueProcessingThread.__init__(self, "Compress thread", queue)
        self.__compressManager = compressManager
        self.__ftp = FTPClient()
        self.__callback = callback
    
    def processElement(self, data):
        """
        Sube y baja imagenes del repositorio, comprimiendo o descromiendo en cada caso
        Args:
            data: es un diccionario que tiene las siguientes claves
                - download: booleano que dice si hay que bajarse una imagen (True) o subirla (False)
                - ftpIP: la dirección IP del servidor FTP
                - ftpPort: el puerto de escucha del servidor FTP
                - ftpUser: nombre de usuario del servidor FTP
                - ftpPassword: la contraseña del servidor FTP
                - filename: lista de archivos a descargar/subir
                - outputPath: ruta donde descomprimir el archivo (donwload = False)
                              crear del archivo comprimido (donwload = True)
        Returns:
            Nothing
        """
        
        if (data["download"]) :
            # Creo el archivo comprimido y añado todos los archivos
            compressFile = self.__compressManager(data["outputPath"], "w")
            for (inputFile, compressName) in data["inputFiles"] :
                compressFile.addFile(inputFile, compressName)
            # Envio el archivo creado por FTP
            self.__ftp.connect(data["ftpIP"], data["ftpPort"], data["timeout"], data["ftpUser"], data["ftpPassword"])
            self.__ftp.storeFile(data["filename"], data["outputPath"])
            self.__ftp.disconnect()
            # Borro el archivo creado
            os.remove(data["outputPath"])
            
            if (self.__callback) :
                self.__callback.downloadedImage()
        else :
            # Me conecto al servidor FTP para bajarme el archivo
            self.__ftp.connect(data["ftpIP"], data["ftpPort"], data["timeout"], data["ftpUser"], data["ftpPassword"])
            self.__ftp.retrieveFile(data["filename"], data["outputPath"])
            self.__ftp.disconnect()
            # Descomprimo el archivo
            compressFile = self.__compressManager(data["filename"], "r")
            compressFile.extract(data["outputPath"])
            # Borro el archivo bajado
            os.remove(os.path.join(data["outputPath"], data["filename"]))
            
            if (self.__callback) :
                self.__callback.uploadedImage()
                
        