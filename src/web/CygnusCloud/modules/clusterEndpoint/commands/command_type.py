# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: spanishCodesTranslator.py    
    Version: 5.0
    Description: commands enum type
    
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

COMMAND_TYPE = enum("REGISTER_VM_SERVER", "UNREGISTER_OR_SHUTDOWN_VM_SERVER", "BOOTUP_VM_SERVER", 
                     "VM_BOOT_REQUEST", "HALT", "DESTROY_DOMAIN", "REBOOT_DOMAIN", "VM_SERVER_CONFIGURATION_CHANGE", "DEPLOY_IMAGE", "DELETE_IMAGE",
                     "CREATE_IMAGE", "EDIT_IMAGE", "DELETE_IMAGE_FROM_INFRASTRUCTURE", "AUTO_DEPLOY_IMAGE")