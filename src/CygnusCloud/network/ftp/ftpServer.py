from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, ThrottledDTPHandler
from pyftpdlib.servers import FTPServer
from network.interfaces.ipAddresses import get_ip_address
from threading import Thread, Lock, Event
from ccutils.processes.childProcessManager import ChildProcessManager
from re import sub    
    
from time import sleep
        
class FTPServerThread(Thread):

    def __init__(self, ftpServer):
        Thread.__init__(self)
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
        
    def startListenning(self, networkInterface, port, maxConnections, maxConnectionsPerIP, downloadBandwidthRatio=0.8, uploadBandwitdhRatio=0.8):
        ip_address = get_ip_address(networkInterface)
        handler = FTPHandler
        handler.authorizer = self.__authorizer
        handler.banner = self.__banner  
        link_bandwidth = ChildProcessManager.runCommandInForeground("ethtool eth0 | grep -i Speed | cut -b 9-", Exception)
        link_bandwidth = int(sub('[^0-9]', '', link_bandwidth))
        dtp_handler = ThrottledDTPHandler
        dtp_handler.read_limit = link_bandwidth * downloadBandwidthRatio * 1024 * 1024
        dtp_handler.write_limit = link_bandwidth * uploadBandwitdhRatio * 1024 * 1024 
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
            - "l" = list files (LIST, NLST, STAT, MLSD, MLST, SIZE, MDTM commands)
            - "r" = retrieve file from the server (RETR command)
           
           Write permissions:
            - "a" = append data to an existing file (APPE command)
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
    ftpServer.startListenning("eth0", 2121, 5, 1, 80)
    ftpServer.addUser("cygnuscloud", "cygnuscloud", "/home/luis/FTPTests", "elradfmwM")
    sleep(5)
    ftpServer.stopListenning()
    