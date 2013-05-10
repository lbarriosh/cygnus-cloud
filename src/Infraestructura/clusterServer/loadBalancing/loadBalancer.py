# -*- coding: utf8 -*-
'''
Basic load balancer definitions

@author: Luis Barrios Hernández
@version: 1.1
'''

from ccutils.enums import enum

MODE_T = enum("BOOT_DOMAIN", "CREATE_OR_EDIT_IMAGE", "DEPLOY_IMAGE")

class LoadBalancer(object):    
    
    '''
    These objects determine the virtual machine server that will host
    a virtual machine.
    '''
    def __init__(self, databaseConnector):
        '''
        Initializes the load balancer's state
        Args:
            databaseConnector: a connector to the main server database
        '''
        self._dbConnector = databaseConnector    
        
    def assignVMServer(self, imageID, mode):
        '''
        Determines what virtual machine server will host an image.
        Args:
            imageID: the image's ID
        Returns:
            a tuple (ID, errorMessage), where ID is the virtual machine server's ID
            and errorMessage is an error message.
        '''
        raise NotImplementedError
    
    def assignVMServers(self, imageID):
        raise NotImplementedError
    
    
