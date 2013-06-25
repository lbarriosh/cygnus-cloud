# -*- coding: utf8 -*-
'''
Created on May 10, 2013

@author: luis
'''
from ccutils.enums import enum

ERROR_DESC_T = enum ("IR_IMAGE_DELETED", # La imagen ha sido borrada del repositorio
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
                "CLSRVR_NOT_EDITED_IMAGE", # La imagen no se está editando
                "CLSRVR_AUTODEPLOYED", # El despliegue automático de la imagen ya ha empezado
                "CLSRVR_AUTOD_TOO_MANY_INSTANCES", # El despliegue automático no puede darnos tantas instancias
                "CLSRVR_LOCKED_IMAGE", # La imagen ya se está editando, por lo que no se puede borrar
                "CLSRVR_DELETED_IMAGE", # La imagen ya se está borrando, por lo que no se puede borrar
                "CLSRVR_UNKNOWN_IMAGE", # El servidor de cluster no sabe cuál es la imagen
                "CLSRVR_IR_CONNECTION_ERROR", # Se ha perdido la conexión con el repositorio
                "CLSRVR_IR_NO_DISK_SPACE", # No hay suficiente espacio en disco en el repositorio
                "CLSRVR_UNKNOWN_VMSRVR", # El servidor de máquinas virtuales no está registrado
                "CLSRVR_VMSRVR_NOT_READY", # El servidor de máquinas virtuales no está preparado
                "CLSRVR_IMAGE_HOSTED_ON_VMSRVR", # El servidor de máquinas virtuales ya tiene la imagen
                "CLSRVR_IMAGE_NOT_HOSTED_ON_VMSRVR", # El servidor de máquinas virtuales no tiene la imagen
                "CLSRVR_VMSRVR_NO_DISK_SPACE", # No hay suficiente espacio en disco en el servidor de máquinas virtuales
                "CLSRVR_VMSRVR_CONNECTION_ERROR", # Error al establecer la conexión con el servidor de máquinas virtuales
                "CLSRVR_VMSRVR_CONNECTION_LOST", # Se ha perdido la conexión con el servidor de máquinas virtuales
                "CLSRVR_DOMAIN_NOT_REGISTERED", # El servidor de cluster no tiene constancia de la existencia de un dominio
                "CLSRVR_ACTIVE_VMSRVR", # El servidor de máquinas virtuales ya está activo, por lo que no podemos editar sus datos
                "CLSRVR_VMSRVR_IDS_IN_USE", # El nombre o la IP y el puerto del servidor de máquinas virtuales ya se están usando
                "CLSRVR_AUTOD_ERROR", # Error de despliegue automático en algunos servidores de máquinas virtuales
                "CLSRVR_VM_BOOT_TIMEOUT", # Timeout en el arranque de una máquina virtual
                "CLSRVR_IMAGE_NOT_AVAILABLE", # La imagen no está disponible
                "CLSRVR_NO_EDITION_SRVRS", # No hay servidores de edición
                "CLSRVR_NO_CANDIDATE_SRVRS", # No hay servidores en los que auto-despliegar la imagen 
                "CLSRVR_EDITION_VMSRVRS_UNDER_FULL_LOAD", # No hay servidor de edición en el que colocar la imagen
                "CLSRVR_VMSRVRS_UNDER_FULL_LOAD", # No hay sitio para colocar la imagen
                )