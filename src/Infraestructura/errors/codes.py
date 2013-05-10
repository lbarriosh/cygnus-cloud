# -*- coding: utf8 -*-
'''
Created on May 10, 2013

@author: luis
'''
from ccutils.enums import enum

ERROR_T = enum ("IR_IMAGE_DELETED", # La imagen ha sido borrada del repositorio
                "IR_UNKNOWN_IMAGE", # La imagen no existe en el repositorio
                "IR_IMAGE_EDITED", # El repositorio sabe que alguien más está editando la imagen
                "IR_NOT_EDITED_IMAGE", # El repositorio sabe que nadie está editando la imagen => no se puede machacar
                "VMSRVR_INTERNAL_ERROR", # Error interno del servidor de máquinas virtuales
                "VMSRVR_UNKNOWN_IMAGE", # El servidor de máquinas virtuales no conoce la imagen
                "VMSRVR_LOCKED_IMAGE", # La imagen se está editando, por lo que no se puede borrar
                "VMSRVR_COMPRESSION_ERROR", # Error al comprimir o descomprimir la imagen
                "VMSRVR_IR_CONNECTION_ERROR", # No se puede establecer la conexión con el repositorio
                "VMSRVR_RETR_TRANSFER_ERROR", # Error al realizar la transferencia FTP RETR
                "VMSRVR_STOR_TRANSFER_ERROR", # Error al realizar la transferencia FTP RETR
                )