# -*- coding: utf8 -*-
'''
Created on May 31, 2013

@author: luis
'''

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.servers import FTPServer
from pyftpdlib.handlers import ThrottledDTPHandler
from network.interfaces.ipAddresses import get_ip_address
from ccutils.processes.childProcessManager import ChildProcessManager
from re import sub  
from network.ftp.pyftpdlibInteraction.ccFTPHandler import CygnusCloudFTPHandler

class ConfigurableFTPServer(object):
    """
    Clase para el servidor FTP basado en pyftpdlib
    """    
    
    def __init__(self, banner):
        """
        Inicializa el estado del servidor
        Argumentos:
            banner: mensaje que se mostrará cuando los usuarios inicien sesión
        """
        self.__authorizer = DummyAuthorizer()       
        self.__banner = banner 
        self.__thread = None        
    
    def startListenning(self, networkInterface, port, maxConnections, maxConnectionsPerIP, ftpCallback = None,
                        downloadBandwidthRatio=0.8, uploadBandwitdhRatio=0.8):
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
        ip_address = get_ip_address(networkInterface)
        handler = CygnusCloudFTPHandler
        handler.ftpCallback = ftpCallback
        handler.authorizer = self.__authorizer
        handler.banner = self.__banner  
        link_bandwidth = ChildProcessManager.runCommandInForeground("/sbin/ethtool eth0 | grep -i Speed | cut -b 9-", Exception)
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
    
    def addUser(self, username, password, homedir, permissions):
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
        self.__authorizer.add_user(username, password, homedir, permissions)        
    
    def removeUser(self, username):
        """
        Elimina un usuario del servidor FTP
        Argumentos:
            username: el nombre del usuario a eliminar
        Devuelve:
            Nada
        """
        self.__authorizer.remove_user(username)        
    
    def stopListenning(self):
        """
        Detiene ordenadamente el servidor FTP
        """
        if (self.__thread == None) :
            raise Exception("The FTP server is not running")
        self.__thread.stop()
