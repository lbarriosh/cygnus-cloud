# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: childProcessManager.py    
    Version: 3.0
    Description: child process manager definitions
    
    Copyright 2012-13 Luis Barrios Hernández, Adrián Fernández Hernández,
        Samuel Guayerbas Martín

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

from subprocess import Popen, PIPE, STDOUT

from ccutils.passwords.rootPasswordHandler import RootPasswordHandler
from ccutils.dataStructures.multithreadingList import GenericThreadSafeList
from ccutils.processes.backgroundPollingThread import BackgroundProcessesPollingThread
from time import sleep

class ChildProcessManager(object):
    """
    These objects create child processes and manage their
    return values.
    """
    def __init__(self):
        """
        Initializes the manager's state
        Args:
            None
        """
        self.__backgroundProcesses = GenericThreadSafeList()
        self.__thread = BackgroundProcessesPollingThread(self.__backgroundProcesses)
        self.__thread.start()
        
    def waitForBackgroundChildrenToTerminate(self):
        """
        Waits for all the child processes running in background to terminate.
        Args:
            None
        Returns:
            Nothing
        """
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
        if (code != 0 and ExceptionClass != None) :            
            raise ExceptionClass(p.stdout.read())  
        else :
            return p.stdout.read()
        
    def runCommandInBackground(self, cmd):
        """
        Runs a command in background
            Args:
                cmd: a string with the command's name and its arguments
            Returns:
                the child process' PID
        """
        p = Popen(cmd, shell=False, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        self.__backgroundProcesses.append(p)
        return p.pid
    
    @staticmethod
    def terminateProcess(pid, ExceptionClass):
        """
        Sends a SIGTERM signal to a process
        Args:
            pid: a process' PID
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