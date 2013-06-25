# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: spanishCodesTranslator.py    
    Version: 5.0
    Description: command outputs enum type
    
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

COMMAND_OUTPUT_TYPE = enum("VM_SERVER_REGISTRATION_ERROR", "VM_SERVER_BOOTUP_ERROR", 
                           "VM_CONNECTION_DATA", "VM_BOOT_FAILURE", "VM_SERVER_UNREGISTRATION_ERROR",
                           "VM_SERVER_SHUTDOWN_ERROR", "DOMAIN_DESTRUCTION_ERROR", "DOMAIN_REBOOT_ERROR",  
                           "VM_SERVER_CONFIGURATION_CHANGE_ERROR", "CONNECTION_ERROR", "COMMAND_TIMED_OUT", 
                           "IMAGE_DEPLOYMENT_ERROR", "DELETE_IMAGE_FROM_SERVER_ERROR", "IMAGE_CREATION_ERROR", 
                           "IMAGE_EDITION_ERROR", "DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR",
                           "AUTO_DEPLOY_ERROR", "VM_SERVER_INTERNAL_ERROR", "IMAGE_DEPLOYED", "IMAGE_CREATED", 
                           "IMAGE_EDITED", "IMAGE_DELETED")