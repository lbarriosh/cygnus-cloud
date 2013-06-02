'''
Created on Jun 2, 2013

@author: luis
'''
from ccutils.enums import enum

CLUSTER_SERVER_PACKET_T = enum("REGISTER_VM_SERVER", "VM_SERVER_REGISTRATION_ERROR", "QUERY_VM_SERVERS_STATUS",
                            "VM_SERVERS_STATUS_DATA", "QUERY_VM_DISTRIBUTION", "VM_DISTRIBUTION_DATA",
                            "UNREGISTER_OR_SHUTDOWN_VM_SERVER", "BOOTUP_VM_SERVER",
                            "VM_SERVER_BOOTUP_ERROR", "VM_BOOT_REQUEST", "VM_CONNECTION_DATA", "VM_BOOT_FAILURE", 
                            "HALT", "QUERY_ACTIVE_VM_DATA", "ACTIVE_VM_DATA", "COMMAND_EXECUTED", "VM_SERVER_SHUTDOWN_ERROR",
                            "VM_SERVER_UNREGISTRATION_ERROR", "DOMAIN_DESTRUCTION", "DOMAIN_DESTRUCTION_ERROR", 
                            "VM_SERVER_CONFIGURATION_CHANGE", "VM_SERVER_CONFIGURATION_CHANGE_ERROR",
                            "GET_IMAGE", "SET_IMAGE", "QUERY_REPOSITORY_STATUS", "REPOSITORY_STATUS",
                            "DEPLOY_IMAGE", "IMAGE_DEPLOYMENT_ERROR", "IMAGE_DEPLOYED", "DELETE_IMAGE_FROM_SERVER", "DELETE_IMAGE_FROM_SERVER_ERROR",
                            "IMAGE_DELETED", "CREATE_IMAGE", "IMAGE_CREATION_ERROR", "IMAGE_CREATED", "EDIT_IMAGE", "IMAGE_EDITION_ERROR",
                            "DELETE_IMAGE_FROM_INFRASTRUCTURE", "DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR", "AUTO_DEPLOY", "AUTO_DEPLOY_ERROR",
                            "VM_SERVER_INTERNAL_ERROR", "QUERY_VM_SERVERS_RESOURCE_USAGE", "VM_SERVERS_RESOURCE_USAGE")