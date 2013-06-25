# -*- coding: utf8 -*-
'''  
    File: ftpServerThread.py 
    Description: FTP server thread definitions
    
    Copyright 2007-2013 Giampaolo Rodola' <g.rodola@gmail.com>
    
                             All Rights Reserved
    
     Permission is hereby granted, free of charge, to any person
     obtaining a copy of this software and associated documentation
     files (the "Software"), to deal in the Software without
     restriction, including without limitation the rights to use,
     copy, modify, merge, publish, distribute, sublicense, and/or sell
     copies of the Software, and to permit persons to whom the
     Software is furnished to do so, subject to the following
     conditions:
    
     The above copyright notice and this permission notice shall be
     included in all copies or substantial portions of the Software.
    
     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
     EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
     OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
     NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
     HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
     WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
     FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
     OTHER DEALINGS IN THE SOFTWARE.
'''
from threading import Thread, Lock, Event

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
    
    def start(self, timeout=0.001):        
        if self.__serving:
            raise RuntimeError("Server already started")
        if self.__stopped:            
            self.__restart()
        self.__timeout = timeout   
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