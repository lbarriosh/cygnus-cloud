'''
Created on May 19, 2013

@author: luis
'''
from ccutils.enums import enum

EDITION_STATE_T = enum("TRANSFER_TO_VM_SERVER", "VM_ON", "TRANSFER_TO_REPOSITORY", "CHANGES_NOT_APPLIED", "AUTO_DEPLOYMENT", 
                       "AUTO_DEPLOYMENT_ERROR", "NOT_EDITED")