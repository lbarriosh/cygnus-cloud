# -*- coding: utf8 -*-
'''
Tipo enumerado para las cuatro transferencias posibles entre el repositorio de imágenes
y un servidor de máquinas virtuales

@author: luis
'''

from ccutils.enums import enum

TRANSFER_T = enum("CREATE_IMAGE", "EDIT_IMAGE", "DEPLOY_IMAGE", "STORE_IMAGE", "CANCEL_EDITION") 
