from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, ThrottledDTPHandler
from pyftpdlib.servers import FTPServer
from network.interfaces.ipAddresses import get_ip_address
from threading import Thread, Lock, Event
from ccutils.processes.childProcessManager import ChildProcessManager
from re import sub    
from os import remove
    
from time import sleep

class FTPCallback(object):
    def on_disconnect(self):
        raise NotImplementedError

    def on_login(self, username):
        raise NotImplementedError
    
    def on_logout(self, username):
        raise NotImplementedError
    
    def on_f_sent(self, f):
        raise NotImplementedError
    
    def on_f_received(self, f):
        raise NotImplementedError
    
    def on_incomplete_f_sent(self, f):
        raise NotImplementedError
    
    def on_incomplete_f_received(self, f):
        raise NotImplementedError

class CygnusCloudFTPHandler(FTPHandler):
    
    def on_disconnect(self):
        if (CygnusCloudFTPHandler.ftpCallback != None) :
            CygnusCloudFTPHandler.ftpCallback.on_disconnect()

    def on_login(self, username):
        if (CygnusCloudFTPHandler.ftpCallback != None) :
            CygnusCloudFTPHandler.ftpCallback.on_login(username)

    def on_logout(self, username):
        if (CygnusCloudFTPHandler.ftpCallback != None):
            CygnusCloudFTPHandler.ftpCallback.on_logout(username)

    def on_f_sent(self, f):
        if (CygnusCloudFTPHandler.ftpCallback != None) :
            CygnusCloudFTPHandler.ftpCallback.on_f_sent(f)

    def on_f_received(self, f):
        if (CygnusCloudFTPHandler.ftpCallback != None):
            CygnusCloudFTPHandler.ftpCallback.on_f_received(f)

    def on_incomplete_f_sent(self, f):
        if (CygnusCloudFTPHandler.ftpCallback != None):
            CygnusCloudFTPHandler.ftpCallback.on_incomplete_f_sent(f)

    def on_incomplete_f_received(self, f):
        if (CygnusCloudFTPHandler.ftpCallback != None) :
            CygnusCloudFTPHandler.ftpCallback.on_incomplete_f_received(f)
        else :
            remove(f)
        
class FTPServerThread(Thread):

    def __init__(self, ftpServer):
        Thread.__init__(self, name="FTP server thread")
        self.__serving = False
        self.__stopped = False
        self.__lock = Lock()
        self.__flag = Event()
        self.server = ftpServer
        
    def __restart(self):
        Thread.__init__(self)
        self.__serving = False
        self.__stopped = False
        self.__lock = Lock()
        self.__flag = Event()

    @property
    def running(self):
        return self.__serving

    def start(self, timeout=0.001, use_poll=False):
        """
            Start serving until an explicit stop() request.
            Polls for shutdown every 'timeout' seconds.
        """
        if self.__serving:
            raise RuntimeError("Server already started")
        if self.__stopped:            
            self.__restart()
        self.__timeout = timeout
        self.__use_poll = use_poll        
        Thread.start(self)
        self.__flag.wait()

    def run(self):
        self.__serving = True 
        self.__flag.set()
        while self.__serving:
            self.__lock.acquire()
            self.server.serve_forever(timeout=self.__timeout, blocking=False)
            self.__lock.release()
        self.server.close_all()

    def stop(self):
        if not self.__serving:
            raise RuntimeError("Server not started yet")
        self.__serving = False
        self.__stopped = True
        self.join()
        
class ConfigurableFTPServer(object):
    def __init__(self, banner):
        self.__authorizer = DummyAuthorizer()       
        self.__banner = banner 
        self.__thread = None
        
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
    """
    def addUser(self, username, password, homedir, permissions):
        self.__authorizer.add_user(username, password, homedir, permissions)
        
    def removeUser(self, username):
        self.__authorizer.remove_user(username)
        
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
    