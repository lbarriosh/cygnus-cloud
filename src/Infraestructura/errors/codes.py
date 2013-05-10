'''
Created on May 10, 2013

@author: luis
'''
from ccutils.enums import enum

ERROR_T = enum (
                "IMAGE_DELETED", # La imagen ha sido borrada del repositorio
                "UNKNOWN_IMAGE", # La imagen no existe
                "IMAGE_EDITED", # La imagen ya se está editando
                "NOT_EDITED_IMAGE" # La imagen no se está editando, por lo que no se puede machacar
                )