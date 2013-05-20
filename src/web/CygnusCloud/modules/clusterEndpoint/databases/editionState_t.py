'''
Created on May 19, 2013

@author: luis
'''
from ccutils.enums import enum

EDITION_STATE_T = enum("DEPLOYMENT", "VM_ON", "TRANSFER_TO_REPOSITORY", "CHANGES_NOT_APPLIED", "NOT_EDITED")