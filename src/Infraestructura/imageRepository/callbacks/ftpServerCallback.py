# -*- coding: utf8 -*-
'''
Created on May 31, 2013

@author: luis
'''

from network.ftp.ftpCallback import FTPCallback
from os import remove, path
from ccutils.processes.childProcessManager import ChildProcessManager

class FTPServerCallback(FTPCallback):
    """
    Callback que procesará los eventos relacionados con las transferencias FTP
    """   
    def __init__(self, slotCounter, dbConnector):
        """
        Inicializa el estado del callback
        Argumentos:
            slotCounter: contador de slots
            dbConnector: conector con la base de datos
        """
        self.__slotCounter = slotCounter
        self.__dbConnector = dbConnector

    def on_disconnect(self):
        """
        Método que se invocará cuando un cliente se desconecta
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        self.__slotCounter.increment()

    def on_login(self, username):
        """
        Método que se invocará cuando un cliente inicia sesión
        Argumentos:
            username: el nombre del usuario
        Devuelve:
            nada
        """
        pass

    def on_logout(self, username):
        """
        Método que se invocará cuando un cliente cierra sesión
        Argumentos:
            username: el nombre del usuario
        Devuelve:
            Nada
        """
        pass

    def on_file_sent(self, f):
        """
        Método que se invocará cuando uun fichero acaba de transferirse
        Argumentos:
            f: el nombre del fichero
        Devuelve:
            Nada
        """
        pass
    
    def on_file_received(self, f):
        """
        Método que se invocará cuando un fichero acaba de recibirse
        Argumentos:
            f: el nombre del fichero
        Devuelve:
            Nada
        """
        self.__dbConnector.handleFinishedUploadTransfer(f)
    
    def on_incomplete_file_sent(self, f):
        """
        Método que se invocará cuando se interrumpe abruptamente la transferencia
        de un fichero
        Argumentos:
            f: el nombre del fichero
        Devuelve:
            Nada
        """
        pass

    def on_incomplete_f_received(self, f):    
        """
        Método que se invocará cuando se interrumpe abruptamente la subida
        de un fichero
        Argumentos:
            f: el nombre del fichero
        Devuelve:
            Nada
        """
        # Borramos el fichero y su directorio para no dejar mierda    
        remove(f)
        ChildProcessManager.runCommandInForeground("rm -rf " + path.dirname(f), Exception)