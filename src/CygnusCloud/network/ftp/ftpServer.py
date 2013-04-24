# -*- coding: utf8 -*-
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, ThrottledDTPHandler
from pyftpdlib.servers import FTPServer
from network.interfaces.ipAddresses import get_ip_address
from threading import Thread, Lock, Event
from ccutils.processes.childProcessManager import ChildProcessManager
from re import sub    
from os import remove
    
from time import sleep

"""
Callback para los eventos generados por el servidor FTP
"""
class FTPCallback(object):    
    
    """
    Método que se invocará cuando un cliente se desconecta
    Argumentos:
        Ninguno
    Devuelve:
        Nada
    """
    def on_disconnect(self):
        raise NotImplementedError

    """
    Método que se invocará cuando un cliente inicia sesión
    Argumentos:
        username: el nombre del usuario
    Devuelve:
        nada
    """
    def on_login(self, username):
        raise NotImplementedError
    
    """
    Método que se invocará cuando un cliente cierra sesión
    Argumentos:
        username: el nombre del usuario
    Devuelve:
        Nada
    """
    def on_logout(self, username):
        raise NotImplementedError
    
    """
    Método que se invocará cuando uun fichero acaba de transferirse
    Argumentos:
        f: el nombre del fichero
    Devuelve:
        Nada
    """
    def on_file_sent(self, f):
        raise NotImplementedError
    
    """
    Método que se invocará cuando un fichero acaba de recibirse
    Argumentos:
        f: el nombre del fichero
    Devuelve:
        Nada
    """
    def on_file_received(self, f):
        raise NotImplementedError
    
    """
    Método que se invocará cuando se interrumpe abruptamente la transferencia
    de un fichero
    Argumentos:
        f: el nombre del fichero
    Devuelve:
        Nada
    """
    def on_incomplete_file_sent(self, f):
        raise NotImplementedError
    
    """
    Método que se invocará cuando se interrumpe abruptamente la subida
    de un fichero
    Argumentos:
        f: el nombre del fichero
    Devuelve:
        Nada
    """
    def on_incomplete_file_received(self, f):
        raise NotImplementedError

"""
Handler par los eventos generados por el servidor FTP. Sus métodos se limitan
a invocar a los métodos homólogos del callback (si está registrado) y a borrar
la basura que aparezca.
"""
class CygnusCloudFTPHandler(FTPHandler):
    
    """
    Método que se invocará cuando un cliente se desconecta
    Argumentos:
        Ninguno
    Devuelve:
        Nada
    """
    def on_disconnect(self):
        if (CygnusCloudFTPHandler.ftpCallback != None) :
            CygnusCloudFTPHandler.ftpCallback.on_disconnect()

    """
    Método que se invocará cuando un cliente inicia sesión
    Argumentos:
        username: el nombre del usuario
    Devuelve:
        nada
    """
    def on_login(self, username):
        if (CygnusCloudFTPHandler.ftpCallback != None) :
            CygnusCloudFTPHandler.ftpCallback.on_login(username)

    """
    Método que se invocará cuando un cliente cierra sesión
    Argumentos:
        username: el nombre del usuario
    Devuelve:
        Nada
    """
    def on_logout(self, username):
        if (CygnusCloudFTPHandler.ftpCallback != None):
            CygnusCloudFTPHandler.ftpCallback.on_logout(username)

    """
    Método que se invocará cuando uun fichero acaba de transferirse
    Argumentos:
        f: el nombre del fichero
    Devuelve:
        Nada
    """
    def on_file_sent(self, f):
        if (CygnusCloudFTPHandler.ftpCallback != None) :
            CygnusCloudFTPHandler.ftpCallback.on_file_sent(f)

    """
    Método que se invocará cuando un fichero acaba de recibirse
    Argumentos:
        f: el nombre del fichero
    Devuelve:
        Nada
    """
    def on_file_received(self, f):
        if (CygnusCloudFTPHandler.ftpCallback != None):
            CygnusCloudFTPHandler.ftpCallback.on_file_received(f)

    """
    Método que se invocará cuando se interrumpe abruptamente la transferencia
    de un fichero
    Argumentos:
        f: el nombre del fichero
    Devuelve:
        Nada
    """
    def on_incomplete_file_sent(self, f):
        if (CygnusCloudFTPHandler.ftpCallback != None):
            CygnusCloudFTPHandler.ftpCallback.on_incomplete_file_sent(f)

    """
    Método que se invocará cuando se interrumpe abruptamente la subida
    de un fichero. Si no hay callback, se carga los datos recibidos
    Argumentos:
        f: el nombre del fichero
    Devuelve:
        Nada
    """
    def on_incomplete_file_received(self, f):
        if (CygnusCloudFTPHandler.ftpCallback != None) :
            CygnusCloudFTPHandler.ftpCallback.on_incomplete_file_received(f)
        else :
            remove(f)
        
"""
Clase para el hilo que ejecutará el bucle del servidor FTP
"""
class FTPServerThread(Thread):
    """
    Inicializa el estado del hilo
    Argumentos:
        ftpServer: servidor FTP cuyo bucle vamos a ejecutar
    """
    def __init__(self, ftpServer):
        Thread.__init__(self, name="FTP server thread")
        self.__serving = False
        self.__stopped = False
        self.__lock = Lock()
        self.__flag = Event()
        self.server = ftpServer
        
    """
    Reinicia la ejecución del hilo
    Argumentos:
        Ninguno
    Devuelve:
        Nada
    """
    def __restart(self):
        Thread.__init__(self)
        self.__serving = False
        self.__stopped = False
        self.__lock = Lock()
        self.__flag = Event()

    @property
    def running(self):
        return self.__serving

    """
    Inicia la ejecución del hilo
    Argumentos:
        timeout: tiempo durante el que se estará ejecutando el bucle
        del servidor FTP ANTES de comprobar si hay que acabar o no
    Devuelve:
        Nada        
    """
    def start(self, timeout=0.001):
        if self.__serving:
            raise RuntimeError("Server already started")
        if self.__stopped:            
            self.__restart()
        self.__timeout = timeout   
        Thread.start(self)
        self.__flag.wait()

    """
    Ejecuta el bucle del servidor FTP y comprueba si hay que parar o no
    cada timeout segundos.
    Argumentos:
        Ninguno
    Devuelve:
        Nada
    """    
    def run(self):
        self.__serving = True 
        self.__flag.set()
        while self.__serving:
            self.__lock.acquire()
            self.server.serve_forever(timeout=self.__timeout, blocking=False)
            self.__lock.release()
        self.server.close_all()

    """
    Finaliza (ordenadamente) la ejecución del bucle del servidor FTP
    Argumentos:
        Ninguno
    Devuelve:
        Nada
    """
    def stop(self):
        if not self.__serving:
            raise RuntimeError("Server not started yet")
        self.__serving = False
        self.__stopped = True
        self.join()
        
"""
Clase para el servidor FTP basado en pyftpdlib
"""
class ConfigurableFTPServer(object):
    """
    Inicializa el estado del servidor
    Argumentos:
        banner: mensaje que se mostrará cuando los usuarios inicien sesión
    """
    def __init__(self, banner):
        self.__authorizer = DummyAuthorizer()       
        self.__banner = banner 
        self.__thread = None
        
    """
    Arranca el servidor FTP
    Argumentos:
        networkInterface: interfaz de red por la que circulará el tráfico FTP
        port: puerto de escucha del servidor
        maxConnections: número máximo de conexiones simultáneas
        maxConnectionsPerIP: número máximo de conexiones por cliente
        ftpCallback: callback que tratará los eventos generados por el servidor. Si es None,
            no se hará, en general, nada para tratar estos eventos.
        downloadBandwidthRatio: fracción del ancho de banda de bajada que se usará para transportar tráfico FTP
        uploadBandwidthRatio: fracción del ancho de banda de subida que se usará para transportar tráfico FTP.
    Devuelve:
        Nada
    """
    def startListenning(self, networkInterface, port, maxConnections, maxConnectionsPerIP, ftpCallback = None,
                        downloadBandwidthRatio=0.8, uploadBandwitdhRatio=0.8):
        ip_address = get_ip_address(networkInterface)
        handler = CygnusCloudFTPHandler
        handler.ftpCallback = ftpCallback
        handler.authorizer = self.__authorizer
        handler.banner = self.__banner  
        link_bandwidth = ChildProcessManager.runCommandInForeground("ethtool eth0 | grep -i Speed | cut -b 9-", Exception)
        if ("Mb/s" in link_bandwidth) :
            power = 1024 ** 2
        else :
            power = 1024 ** 3
        link_bandwidth = int(sub('[^0-9]', '', link_bandwidth))
        dtp_handler = ThrottledDTPHandler
        dtp_handler.read_limit = link_bandwidth * downloadBandwidthRatio * power
        dtp_handler.write_limit = link_bandwidth * uploadBandwitdhRatio * power 
        handler.dtp_handler = dtp_handler
        address = (ip_address, port)
        self.__ftpServer = FTPServer(address, handler)
        self.__ftpServer.max_cons = maxConnections
        self.__ftpServer.max_cons_per_ip = maxConnectionsPerIP
        self.__thread = FTPServerThread(self.__ftpServer)
        self.__thread.start()
        
    """
    Añade un usuario al servidor FTP
    Argumentos:
        username: nombre del usuario
        password: contraseña del usuario
        homedir: directorio raíz del servidor que verá el usuario
        permissions: string con los permisos del usuario. Se construye de la siguiente manera:
            Read permissions:
                - "e" = change directory (CWD command)
                - "l" = list filess (LIST, NLST, STAT, MLSD, MLST, SIZE, MDTM commands)
                - "r" = retrieve files from the server (RETR command)
               
               Write permissions:
                - "a" = append data to an existing f (APPE command)
                - "d" = delete file or directory (DELE, RMD commands)
                - "f" = rename file or directory (RNFR, RNTO commands)
                - "m" = create directory (MKD command)
                - "w" = store a file to the server (STOR, STOU commands)
                - "M" = change file mode (SITE CHMOD command)
    Devuelve:
        Nada
    """
    def addUser(self, username, password, homedir, permissions):
        self.__authorizer.add_user(username, password, homedir, permissions)
        
    """
    Elimina un usuario del servidor FTP
    Argumentos:
        username: el nombre del usuario a eliminar
    Devuelve:
        Nada
    """
    def removeUser(self, username):
        self.__authorizer.remove_user(username)
        
    """
    Detiene ordenadamente el servidor FTP
    """
    def stopListenning(self):
        if (self.__thread == None) :
            raise Exception("The FTP server is not running")
        self.__thread.stop()
        
if __name__ == "__main__" :
    ftpServer = ConfigurableFTPServer("Welcome to the image repository FTP server!")
    ftpServer.startListenning("lo", 2121, 5, 1)
    ftpServer.addUser("cygnuscloud", "cygnuscloud", "/home/luis/Pictures", "elradfmwM")
    sleep(5)
    ftpServer.stopListenning()    