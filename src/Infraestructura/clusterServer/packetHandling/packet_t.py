# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: packet_t.py    
    Version: 5.0
    Description: cluster server packet types definition
    
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

CLUSTER_SERVER_PACKET_T = enum("REGISTER_VM_SERVER", "VM_SERVER_REGISTRATION_ERROR", "QUERY_VM_SERVERS_STATUS",
                            "VM_SERVERS_STATUS_DATA", "QUERY_VM_DISTRIBUTION", "VM_DISTRIBUTION_DATA",
                            "UNREGISTER_OR_SHUTDOWN_VM_SERVER", "BOOTUP_VM_SERVER",
                            "VM_SERVER_BOOTUP_ERROR", "VM_BOOT_REQUEST", "VM_CONNECTION_DATA", "VM_BOOT_FAILURE", 
                            "HALT", "QUERY_ACTIVE_VM_VNC_DATA", "ACTIVE_VM_VNC_DATA", "COMMAND_EXECUTED", "VM_SERVER_SHUTDOWN_ERROR",
                            "VM_SERVER_UNREGISTRATION_ERROR", "DOMAIN_DESTRUCTION", "DOMAIN_DESTRUCTION_ERROR", 
                            "VM_SERVER_CONFIGURATION_CHANGE", "VM_SERVER_CONFIGURATION_CHANGE_ERROR",
                            "GET_IMAGE", "SET_IMAGE", "QUERY_REPOSITORY_STATUS", "REPOSITORY_STATUS",
                            "DEPLOY_IMAGE", "IMAGE_DEPLOYMENT_ERROR", "IMAGE_DEPLOYED", "DELETE_IMAGE_FROM_SERVER", "DELETE_IMAGE_FROM_SERVER_ERROR",
                            "IMAGE_DELETED", "CREATE_IMAGE", "IMAGE_CREATION_ERROR", "IMAGE_CREATED", "EDIT_IMAGE", "IMAGE_EDITION_ERROR",
                            "DELETE_IMAGE_FROM_INFRASTRUCTURE", "DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR", "AUTO_DEPLOY", "AUTO_DEPLOY_ERROR",
                            "VM_SERVER_INTERNAL_ERROR", "QUERY_VM_SERVERS_RESOURCE_USAGE", "VM_SERVERS_RESOURCE_USAGE",
                            "DOMAIN_REBOOT", "DOMAIN_REBOOT_ERROR")