# -*- coding: utf8 -*-
'''
Created on May 31, 2013

@author: luis
'''

from pyftpdlib.handlers import FTPHandler
from os import remove

class CygnusCloudFTPHandler(FTPHandler):
    """
    Handler par los eventos generados por el servidor FTP. Sus métodos se limitan
    a invocar a los métodos homólogos del callback (si está registrado) y a borrar
    la basura que aparezca.
    """    
    
    def on_disconnect(self):
        """
        Método que se invocará cuando un cliente se desconecta
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        if (CygnusCloudFTPHandler.ftpCallback != None) :
            CygnusCloudFTPHandler.ftpCallback.on_disconnect()
    
    def on_login(self, username):
        """
        Método que se invocará cuando un cliente inicia sesión
        Argumentos:
            username: el nombre del usuario
        Devuelve:
            nada
        """
        if (CygnusCloudFTPHandler.ftpCallback != None) :
            CygnusCloudFTPHandler.ftpCallback.on_login(username)
    
    def on_logout(self, username):
        """
        Método que se invocará cuando un cliente cierra sesión
        Argumentos:
            username: el nombre del usuario
        Devuelve:
            Nada
        """
        if (CygnusCloudFTPHandler.ftpCallback != None):
            CygnusCloudFTPHandler.ftpCallback.on_logout(username)
    
    def on_file_sent(self, f):
        """
        Método que se invocará cuando uun fichero acaba de transferirse
        Argumentos:
            f: el nombre del fichero
        Devuelve:
            Nada
        """
        if (CygnusCloudFTPHandler.ftpCallback != None) :
            CygnusCloudFTPHandler.ftpCallback.on_file_sent(f)
    
    def on_file_received(self, f):
        """
        Método que se invocará cuando un fichero acaba de recibirse
        Argumentos:
            f: el nombre del fichero
        Devuelve:
            Nada
        """
        if (CygnusCloudFTPHandler.ftpCallback != None):
            CygnusCloudFTPHandler.ftpCallback.on_file_received(f)
    
    def on_incomplete_file_sent(self, f):
        """
        Método que se invocará cuando se interrumpe abruptamente la transferencia
        de un fichero
        Argumentos:
            f: el nombre del fichero
        Devuelve:
            Nada
        """
        if (CygnusCloudFTPHandler.ftpCallback != None):
            CygnusCloudFTPHandler.ftpCallback.on_incomplete_file_sent(f)
    
    def on_incomplete_file_received(self, f):
        """
        Método que se invocará cuando se interrumpe abruptamente la subida
        de un fichero. Si no hay callback, se carga los datos recibidos
        Argumentos:
            f: el nombre del fichero
        Devuelve:
            Nada
        """
        if (CygnusCloudFTPHandler.ftpCallback != None) :
            CygnusCloudFTPHandler.ftpCallback.on_incomplete_file_received(f)
        else :
            remove(f)        