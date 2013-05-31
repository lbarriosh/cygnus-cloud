'''
Created on May 31, 2013

@author: luis
'''
from threading import Thread, Lock, Event

class FTPServerThread(Thread):
    """
    Clase para el hilo que ejecutará el bucle del servidor FTP
    """
    
    def __init__(self, ftpServer):
        """
        Inicializa el estado del hilo
        Argumentos:
            ftpServer: servidor FTP cuyo bucle vamos a ejecutar
        """
        Thread.__init__(self, name="FTP server thread")
        self.__serving = False
        self.__stopped = False
        self.__lock = Lock()
        self.__flag = Event()
        self.server = ftpServer        
    
    def __restart(self):
        """
        Reinicia la ejecución del hilo
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        Thread.__init__(self)
        self.__serving = False
        self.__stopped = False
        self.__lock = Lock()
        self.__flag = Event()

    @property
    def running(self):
        return self.__serving
    
    def start(self, timeout=0.001):
        """
        Inicia la ejecución del hilo
        Argumentos:
            timeout: tiempo durante el que se estará ejecutando el bucle
            del servidor FTP ANTES de comprobar si hay que acabar o no
        Devuelve:
            Nada        
        """
        if self.__serving:
            raise RuntimeError("Server already started")
        if self.__stopped:            
            self.__restart()
        self.__timeout = timeout   
        Thread.start(self)
        self.__flag.wait()
    
    def run(self):
        """
        Ejecuta el bucle del servidor FTP y comprueba si hay que parar o no
        cada timeout segundos.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """    
        self.__serving = True 
        self.__flag.set()
        while self.__serving:
            self.__lock.acquire()
            self.server.serve_forever(timeout=self.__timeout, blocking=False)
            self.__lock.release()
        self.server.close_all()
            
    def stop(self):
        """
        Finaliza (ordenadamente) la ejecución del bucle del servidor FTP
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        if not self.__serving:
            raise RuntimeError("Server not started yet")
        self.__serving = False
        self.__stopped = True
        self.join()        