# -*- coding: utf8 -*-
  
class FTPCallback(object):   
    """
    Callback para los eventos generados por el servidor FTP
    """ 
       
    def on_disconnect(self):
        """
        Método que se invocará cuando un cliente se desconecta
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        raise NotImplementedError
    
    def on_login(self, username):
        """
        Método que se invocará cuando un cliente inicia sesión
        Argumentos:
            username: el nombre del usuario
        Devuelve:
            nada
        """
        raise NotImplementedError    
    
    def on_logout(self, username):
        """
        Método que se invocará cuando un cliente cierra sesión
        Argumentos:
            username: el nombre del usuario
        Devuelve:
            Nada
        """
        raise NotImplementedError    
    
    def on_file_sent(self, f):
        """
        Método que se invocará cuando uun fichero acaba de transferirse
        Argumentos:
            f: el nombre del fichero
        Devuelve:
            Nada
        """
        raise NotImplementedError    
    
    def on_file_received(self, f):
        """
        Método que se invocará cuando un fichero acaba de recibirse
        Argumentos:
            f: el nombre del fichero
        Devuelve:
            Nada
        """
        raise NotImplementedError    
    
    def on_incomplete_file_sent(self, f):
        """
        Método que se invocará cuando se interrumpe abruptamente la transferencia
        de un fichero
        Argumentos:
            f: el nombre del fichero
        Devuelve:
            Nada
        """
        raise NotImplementedError    
    
    def on_incomplete_file_received(self, f):
        """
        Método que se invocará cuando se interrumpe abruptamente la subida
        de un fichero
        Argumentos:
            f: el nombre del fichero
        Devuelve:
            Nada
        """
        raise NotImplementedError