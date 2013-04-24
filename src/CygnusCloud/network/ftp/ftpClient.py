# # -*- coding: utf8 -*-
from ftplib import FTP
import os

"""
Clase para el cliente FTP basado en ftplib
"""
class FTPClient(object):
    """
    Inicializa el estado del cliente
    Argumentos:
        Ninguno
    """
    def __init__(self):
        self.__ftp = FTP()

    """"
    Establece la conexión con el servidor FTP
    Argumentos:
        host: la IP del servidor FTP
        port: el puerto de escucha del servidor FTP
        timeout: timeout máximo (en segundos) para establecer la conexión
        user: usuario a utilizar
        password: contraseña a utilizar
    """
    def connect(self, host, port, timeout, user, password):
        self.__ftp.connect(host, port, timeout)
        self.__ftp.login(user, password)
        self.__ftp.set_pasv(True)
        
    """
    Almacena un fichero en el servidor FTP
    Argumentos:
        fileName: nombre (OJO, solo nombre) del fichero a subir
        localDirectory: directorio LOCAL en el que está el fichero a subir
        serverDirectory: directorio del servidor al que queremos subir el fichero. Si es None,
        se guardará en la raíz.
    Devuelve:
        Nada
    """
    def storeFile(self, fileName, localDirectory, serverDirectory=None):
        if (serverDirectory != None) :
            self.__ftp.cwd(serverDirectory)        
        self.__ftp.storbinary("STOR " + fileName, open(os.path.join(localDirectory, fileName), "rb"))
        
    """
    Descarga un fichero del servidor FTP
    Argumentos:
        fileName: nombre (OJO, solo nombre) del fichero a descargar
        localDirectory: directorio LOCAL en el que estará el fichero a descargar
        serverDirectory: directorio del servidor en el que está el fichero a descargar. Si es None,
        se asumirá que el fichero está en la raíz
    Devuelve:
        Nada
    """
    def retrieveFile(self, fileName, localDirectory, serverDirectory=None):
        if (serverDirectory != None) :
            self.__ftp.cwd(serverDirectory)
        with open(os.path.join(localDirectory, fileName), "wb") as f:
            def ftpCallback(data):
                f.write(data)
            self.__ftp.retrbinary("RETR " + fileName, ftpCallback)
        
    """
    Cierra educadamente la conexión con el servidor FTP
    Argumentos:
        Ninguno
    Devuelve:
        Nada
    """
    def disconnect(self):
        self.__ftp.quit()
        
if __name__ == "__main__" :
    ftpClient = FTPClient()
    ftpClient.connect("127.0.0.1", 2121, 100, "cygnuscloud", "cygnuscloud")
    ftpClient.retrieveFile("earth-horizon.jpg", "/home/luis")