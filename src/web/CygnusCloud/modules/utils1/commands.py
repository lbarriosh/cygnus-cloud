# -*- coding: utf8 -*-
'''
A module that contains useful functions to run commands
@author: Luis Barrios Hernández
@author: Samuel Guayerbas
@version: 2.0
'''

from subprocess import Popen, PIPE, STDOUT

def runCommand(cmd, ExceptionClass):
        """
        Runs a command
        Args:
            cmd: the command to run
        Returns:
            The run command's output
        Raises:
            ExceptionClass: this exception will be raised if something goes
            wrong when running the command.
        """
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        # Wait until the command finishes
        code = p.wait()
        if (code != 0) :
            # Something went wrong => raise an exception
            raise ExceptionClass(p.stdout.read())  
        else :
            # Return the command's output
            return p.stdout.read()

def runCommandBackground(cmd):
        """
        Runs a command in background
        Args:
            cmd: the command to run in background
        Returns:
            cmd's command
        """
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        return p.pid