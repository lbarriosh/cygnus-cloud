# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: errors.py    
    Version: 1.5
    Description: error codes definition
    
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

ERROR_DESC_T = enum ("IR_IMAGE_DELETED", # The image was deleted from the image repository
                "IR_UNKNOWN_IMAGE", # The image does not exist in the image repository
                "IR_IMAGE_EDITED", # Someone is already editing the image
                "IR_NOT_EDITED_IMAGE", # The image is not being edited. Therefore, an updated copy of it cannot be uploaded to the image repository.
                "VMSRVR_INTERNAL_ERROR", # Internal error at a virtual machine server
                "VMSRVR_UNKNOWN_IMAGE", # The image is not deployed at the virtual machine server.
                "VMSRVR_LOCKED_IMAGE", # The image is being edited, so it can't be deleted.
                "VMSRVR_COMPRESSION_ERROR", # Unable to extract or create a .zip file at a virtual machine server.
                "VMSRVR_IR_CONNECTION_ERROR", # The virtual machine server cannot connect to the image repository.
                "VMSRVR_RETR_TRANSFER_ERROR", # The FTP RETR transfer crashed.
                "VMSRVR_STOR_TRANSFER_ERROR", # The FTP STOR transfer crashed.
                "CLSRVR_NOT_EDITED_IMAGE", # The image is not being edited, 
                "CLSRVR_AUTODEPLOYED", # The automatic deployment of the image has already begun.
                "CLSRVR_AUTOD_TOO_MANY_INSTANCES", # The automatic deployment process cannot create the required instance number.
                "CLSRVR_LOCKED_IMAGE", # The image is already being edited, so it can't be deleted.
                "CLSRVR_DELETED_IMAGE", # The image is already being deleted, so it can't be deleted.
                "CLSRVR_UNKNOWN_IMAGE", # The image is not registered at the cluster server.
                "CLSRVR_IR_CONNECTION_ERROR", # The cluster server cannot connect to the image repository.
                "CLSRVR_IR_NO_DISK_SPACE", # There's not enough disk space at the image repository.
                "CLSRVR_UNKNOWN_VMSRVR", # The requested virtual machine server is not registered.
                "CLSRVR_VMSRVR_NOT_READY", # The requested virtual machine server is not ready yet.
                "CLSRVR_IMAGE_HOSTED_ON_VMSRVR", # The requested virtual machine server already stores the image.
                "CLSRVR_IMAGE_NOT_HOSTED_ON_VMSRVR", # The requested virtual machine server does not store the image.
                "CLSRVR_VMSRVR_NO_DISK_SPACE", # There's not enough disk space at the requested virtual machine server.
                "CLSRVR_VMSRVR_CONNECTION_ERROR", # The connnection with the requested virtual machine server cannot be established.
                "CLSRVR_VMSRVR_CONNECTION_LOST", # The connnection with the requested virtual machine server was lost.
                "CLSRVR_DOMAIN_NOT_REGISTERED", # The virtual machine is not registered on the cluster server.
                "CLSRVR_ACTIVE_VMSRVR", # The requested virtual machine server is already on. Therefore, its basic configuration cannot be changed.
                "CLSRVR_VMSRVR_IDS_IN_USE", # The virtual machine server's new name or IP address are already in use.
                "CLSRVR_AUTOD_ERROR", # The auto deployment operation crashed on several virtual machine servers.,
                "CLSRVR_VM_BOOT_TIMEOUT", # Timeout error on virtual machine boot
                "CLSRVR_IMAGE_NOT_AVAILABLE", # The requested image is not available
                "CLSRVR_NO_EDITION_SRVRS", # There are no edition servers to create or edit the image.
                "CLSRVR_NO_CANDIDATE_SRVRS", # There are no candidate servers to deploy an image.
                "CLSRVR_EDITION_VMSRVRS_UNDER_FULL_LOAD", # There are not enough edition servers to perform the requested operation.
                "CLSRVR_VMSRVRS_UNDER_FULL_LOAD", # There are not enough virtual machine servers to perform the requested operation.
                )