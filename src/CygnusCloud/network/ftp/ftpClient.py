# # -*- coding: utf8 -*-
from ftplib import FTP
import os

class FTPClient(object):
    def __init__(self):
        self.__ftp = FTP()
    
    def connect(self, host, port, timeout, user, password):
        self.__ftp.connect(host, port, timeout)
        self.__ftp.login(user, password)
        self.__ftp.set_pasv(True)
        
    def storeFile(self, fileName, localDirectory, serverDirectory=None):
        if (serverDirectory != None) :
            self.__ftp.cwd(serverDirectory)        
        self.__ftp.storbinary("STOR " + fileName, open(os.path.join(localDirectory, fileName), "rb"))
        
    def retrieveFile(self, fileName, localDirectory, serverDirectory=None):
        if (serverDirectory != None) :
            self.__ftp.cwd(serverDirectory)
        with open(os.path.join(localDirectory, fileName), "wb") as f:
            def ftpCallback(data):
                f.write(data)
            self.__ftp.retrbinary("RETR " + fileName, ftpCallback)
        
    def disconnect(self):
        self.__ftp.quit()
        
if __name__ == "__main__" :
    ftpClient = FTPClient()
    ftpClient.connect("127.0.0.1", 2121, 100, "cygnuscloud", "cygnuscloud")
    ftpClient.retrieveFile("earth-horizon.jpg", "/home/luis")