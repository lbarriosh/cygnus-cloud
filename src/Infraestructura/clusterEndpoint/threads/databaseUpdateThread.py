# -*- coding: utf8 -*-
'''
Definiciones del hilo de actualización periódica de la base de datos de estado
@author: Luis Barrios Hernández
@version: 1.1
'''

from ccutils.threads import BasicThread

from time import sleep

class UpdateHandler(object):
    """
    Interfaz utilizada para realizar la actualización de la base de datos de estado
    """
    def sendUpdateRequestPackets(self):
        """
        Envía las peticiones de actualización al servidor de cluster
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        raise NotImplementedError

class VMServerMonitoringThread(BasicThread):
    """
    Estos hilos refrescan la base de datos de estado periódicamente.
    """
    def __init__(self, updateHandler, sleepTime):
        """
        Inicializa el estado
        Argumentos:
            updateHandler: el objeto que envía los paquetes para obtener la información
            sleepTime: tiempo (en segundos) que separa dos actualizaciones consecutivas.
        """
        BasicThread.__init__(self, "Status database update thread")
        self.__handler = updateHandler
        self.__sleepTime = sleepTime
        
    def run(self):
        """
        Envía los paquetes de actualización del estado
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        while not self.finish() :
            self.__handler.sendUpdateRequestPackets()
            sleep(self.__sleepTime)