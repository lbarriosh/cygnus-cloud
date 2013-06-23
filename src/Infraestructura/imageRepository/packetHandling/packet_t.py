# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: packet_t.py    
    Version: 2.0
    Description: image repository packet types definition
    
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


PACKET_T = enum("HALT", "ADD_IMAGE", "ADDED_IMAGE_ID", "RETR_REQUEST", "RETR_REQUEST_RECVD", 
                "RETR_REQUEST_ERROR", "RETR_START", "RETR_ERROR", "STOR_REQUEST", 
                "STOR_REQUEST_RECVD", "STOR_REQUEST_ERROR", "STOR_START", "STOR_ERROR",
                "DELETE_REQUEST", "DELETE_REQUEST_RECVD", "DELETE_REQUEST_ERROR", 
                "STATUS_REQUEST", "STATUS_DATA", "CANCEL_EDITION", "IMAGE_EDITION_CANCELLED")