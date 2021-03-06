# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: editionState_t.py    
    Version: 1.0
    Description: image edition state enum type
    
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

EDITION_STATE_T = enum("TRANSFER_TO_VM_SERVER", "VM_ON", "TRANSFER_TO_REPOSITORY", "CHANGES_NOT_APPLIED", "AUTO_DEPLOYMENT", 
                       "AUTO_DEPLOYMENT_ERROR", "NOT_EDITED")