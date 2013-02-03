# -*- coding: utf8 -*-
'''
A module that contains useful functions to run commands
@author: Luis Barrios Hernández
@author: Samuel Guayerbas
@version: 2.0
'''

from subprocess import Popen, PIPE, STDOUT

from utils.rootPasswordHandler import RootPasswordHandler

def runCommand(cmd, ExceptionClass):
    """
    Runs a command in foreground
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
    
def runCommandInBackground(cmd):
    """
    Runs a command in background
    Args:
        cmd: the command to run in background
    Returns:
        cmd's command
    """
    print cmd
    p = Popen(cmd, shell=False, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    return p.pid

def runCommandAsRoot(cmd, ExceptionClass):
    """
    Runs a command in foreground and as root
    Args:
        cmd: the command to run
    Returns:
        The run command's output
    Raises:
        ExceptionClass: this exception will be raised if something goes
        wrong when running the command.
    """
    # Get root's password
    password = RootPasswordHandler.getInstance().getRootsPassword()
    # Generate the command's header
    header = "echo " + password + " | sudo -S "
    # Run the command
    return runCommand(header + cmd, ExceptionClass)