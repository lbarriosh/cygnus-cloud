# -*- coding: utf8 -*-
'''
Child process manager definitios
@author: Luis Barrios Hernández
@author: Samuel Guayerbas
@version: 3.0
'''

from subprocess import Popen, PIPE, STDOUT

from ccutils.rootPasswordHandler import RootPasswordHandler
from ccutils.dataStructures.multithreadingList import GenericThreadSafeList
from ccutils.processes.backgroundPollingThread import BackgroundProcessesPollingThread
from time import sleep

class ChildProcessManager(object):
    """
    These objects create child processes and manage their
    return values.
    """
    def __init__(self):
        self.__backgroundProcesses = GenericThreadSafeList()
        self.__thread = BackgroundProcessesPollingThread(self.__backgroundProcesses)
        self.__thread.start()
        
    def waitForBackgroundChildrenToTerminate(self):
        self.__thread.stop()
        while not self.__thread.finish() :
            sleep(0.1)
          
    @staticmethod  
    def runCommandInForeground(cmd, ExceptionClass):
        """
        Runs a command in foreground
        Args:
            cmd: a string with the command's name and its arguments
            ExceptionClass: the exception that will be raised if something goes wrong
        Returns:
            The run command's output
        Raises:
            ExceptionClass: this exception will be raised if something goes
            wrong when running the command.
        """
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        code = p.wait()
        if (code != 0) :            
            raise ExceptionClass(p.stdout.read())  
        else :
            return p.stdout.read()
        
    def runCommandInBackground(self, cmd):
        """
        Runs a command in background
            Args:
                cmd: a string with the command's name and its arguments
            Returns:
                a PID
        """
        p = Popen(cmd, shell=False, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        self.__backgroundProcesses.append(p)
        return p.pid
    
    @staticmethod
    def terminateProcess(pid, ExceptionClass):
        """
        Sends a SIGTERM signal to a process
        Args:
            pid: A PID
            ExceptionClass: the exception that will be raised if something goes wrong
        Returns :
            Nothing
        Raises:
            ExceptionClass: this exception will be raised if something goes
            wrong while killing the process.
        """        
        ChildProcessManager.runCommandInForeground(["kill -s TERM " + str(pid)], ExceptionClass)
        
    @staticmethod
    def runCommandInForegroundAsRoot(cmd, ExceptionClass):
        """
        Runs a command in foreground and as the super-user.
        Args:
            cmd: a string with the command's name and its arguments
            ExceptionClass: the exception that will be raised if something goes wrong
        Returns:
            The run command's output
        Raises:
            ExceptionClass: this exception will be raised if something goes
            wrong when running the command.
        """ 
        password = RootPasswordHandler().getRootsPassword()
        header = "echo " + password + " | sudo -S "
        return ChildProcessManager.runCommandInForeground(header + cmd, ExceptionClass)