# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: loadBalancer.py    
    Version: 1.1
    Description: load balancer interface definitions
    
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

from ccutils.enums import enum

MODE_T = enum("BOOT_DOMAIN", "CREATE_OR_EDIT_IMAGE", "DEPLOY_IMAGE")

class LoadBalancer(object):       
    '''
    This class defines the interface common to all the load balancing algorithms.
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
            mode: the operation that the virtual machine server will perform (i.e. boot a virtual
                machine that uses the specified image, deploy an image,...)
        Returns:
            a tuple (server IDs, errorMessage, copies), where server IDs is a list containing the
            chosen servers IDs, errorMessage is an error message and copies is the number of
            copies that can be hosted on the chosen servers.
        '''
        raise NotImplementedError
    
    def assignVMServers(self, imageID):
        raise NotImplementedError