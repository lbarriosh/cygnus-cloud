# -*- coding: utf8 -*-
'''
Basic load balancer definitions

@author: Luis Barrios Hernández
@version: 1.1
'''

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
        
    def assignVMServer(self, imageId):
        '''
        Determines what virtual machine server will host an image.
        Args:
            imageId: the image's ID
        Returns:
            a tuple (ID, errorMessage), where ID is the virtual machine server's ID
            and errorMessage is an error message.
        '''
        raise NotImplementedError
