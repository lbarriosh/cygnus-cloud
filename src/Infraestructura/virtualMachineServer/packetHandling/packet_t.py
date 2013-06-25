# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: packet_t.py    
    Version: 6.0
    Description: virtual machine server packet types definition
    
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

VM_SERVER_PACKET_T = enum("CREATE_DOMAIN", "DESTROY_DOMAIN", "REBOOT_DOMAIN", "DOMAIN_CONNECTION_DATA", "SERVER_STATUS",
                          "SERVER_STATUS_REQUEST", "USER_FRIENDLY_SHUTDOWN", 
                          "HALT", "QUERY_ACTIVE_VM_DATA", "ACTIVE_VM_DATA", "QUERY_ACTIVE_DOMAIN_UIDS", "ACTIVE_DOMAIN_UIDS",
                          "IMAGE_EDITION", "IMAGE_EDITION_ERROR", "DEPLOY_IMAGE", "IMAGE_DEPLOYMENT_ERROR","DELETE_IMAGE", "IMAGE_DELETION_ERROR",
                          "IMAGE_EDITED", "IMAGE_DEPLOYED", "IMAGE_DELETED", "INTERNAL_ERROR")