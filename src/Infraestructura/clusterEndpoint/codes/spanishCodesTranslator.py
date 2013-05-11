# -*- coding: utf8 -*
'''
Created on May 11, 2013

@author: luis
'''
from codesTranslator import CodesTranslator

from clusterServer.database.clusterServerDB import SERVER_STATE_T, IMAGE_STATE_T
from errors.codes import ERROR_DESC_T

class SpanishCodesTranslator(CodesTranslator):
    def processVMServerSegment(self, data):
        result = []
        for tup in data :
            tmp = list(tup)
            tmp[1] = self.__translateServerStatusCode(tmp[1])
            result.append(tuple(tmp))
        return result
    
    def processVMDistributionSegment(self, data):
        result = []
        for tup in data :
            tmp = list(tup)
            if (tmp[2] == IMAGE_STATE_T.READY) :
                tmp[2] = "Sincronizada"
            elif (tmp[2] == IMAGE_STATE_T.EDITED) :
                tmp[2] = "No sincronizada"
            elif (tmp[2] == IMAGE_STATE_T.DEPLOY) :
                tmp[2] = "En despliegue"
            else:
                tmp[2] = "Pendiente de borrado"
            result.append(tuple(tmp))
        return result           
    
    def __translateServerStatusCode(self, code):
        if (code == SERVER_STATE_T.BOOTING) :
            return "Arrancando"
        elif (code == SERVER_STATE_T.READY) :
            return "Listo"
        elif (code == SERVER_STATE_T.SHUT_DOWN):
            return "Apagado"
        elif (code == SERVER_STATE_T.RECONNECTING):
            return "Reestableciendo conexión"
        else :
            return "Apagado - Fallo de conexión"         
    
    def translateRepositoryStatusCode(self, code): 
        return self.__translateServerStatusCode(code)
    
    def translateErrorDescriptionCode(self, code):
        if (code == ERROR_DESC_T.IR_IMAGE_DELETED) :
            return "La imagen ya ha sido borrada del repositorio"
        elif (code == ERROR_DESC_T.IR_UNKNOWN_IMAGE) :
            return "La imagen no existe en el repositorio"
        elif (code == ERROR_DESC_T.IR_IMAGE_EDITED or code == ERROR_DESC_T.VMSRVR_LOCKED_IMAGE) :
            return "Otro usuario está editando la imagen"
        elif (code == ERROR_DESC_T.IR_NOT_EDITED_IMAGE or code == ERROR_DESC_T.CLSRVR_NOT_EDITED_IMAGE) :
            return "La imagen no se está editando. No se puede sobreescribir la copia del repositorio"
        elif (code == ERROR_DESC_T.VMSRVR_INTERNAL_ERROR) :
            return "Error interno del servidor de máquinas virtuales"
        elif (code == ERROR_DESC_T.VMSRVR_UNKNOWN_IMAGE or ERROR_DESC_T.CLSRVR_UNKNOWN_IMAGE) :
            return "Imagen desconocida"
        elif (code == ERROR_DESC_T.VMSRVR_COMPRESSION_ERROR) :
            return "Error al comprimir o descomprimir la imagen"
        elif (code == ERROR_DESC_T.VMSRVR_IR_CONNECTION_ERROR or code == ERROR_DESC_T.CLSRVR_IR_CONNECTION_ERROR) :
            return "No se puede establecer la conexión con el repositorio"
        elif (code == ERROR_DESC_T.VMSRVR_RETR_TRANSFER_ERROR) :
            return "Error al realizar la transferencia FTP RETR"
        elif (code == ERROR_DESC_T.VMSRVR_STOR_TRANSFER_ERROR) :
            return "Error al realizar la transferencia FTP STOR"
        elif (code == ERROR_DESC_T.CLSRVR_AUTODEPLOYED):
            return "El despliegue automático de la imagen ya ha comenzado"
        elif (code == ERROR_DESC_T.CLSRVR_AUTOD_TOO_MANY_INSTANCES):
            return "Demasiadas instancias a desplegar"
        elif (code == ERROR_DESC_T.CLSRVR_LOCKED_IMAGE):
            return "La imagen se está editando"
        elif (code == ERROR_DESC_T.CLSRVR_DELETED_IMAGE):
            return "La imagen se está borrando"
        elif (code == ERROR_DESC_T.CLSRVR_IR_NO_DISK_SPACE) :
            return "No hay suficiente espacio en disco en el repositorio"   
        elif (code == ERROR_DESC_T.CLSRVR_UNKNOWN_VMSRVR) :
            return "El servidor de máquinas virtuales no está registrado"    
        elif (code == ERROR_DESC_T.CLSRVR_VMSRVR_NOT_READY) :
            return "El servidor de máquinas virtuales no está listo"    
        elif (code == ERROR_DESC_T.CLSRVR_IMAGE_HOSTED_ON_VMSRVR) :
            return "La imagen ya está desplegada en el servidor de máquinas virtuales"   
        elif (code == ERROR_DESC_T.CLSRVR_IMAGE_NOT_HOSTED_ON_VMSRVR) :
            return "La imagen no está desplegada en el servidor de máquinas virtuales"   
        elif (code == ERROR_DESC_T.CLSRVR_VMSRVR_NO_DISK_SPACE) :
            return "No hay suficiente espacio en disco en el servidor de máquinas virtuales"   
        elif (code == ERROR_DESC_T.CLSRVR_VMSRVR_CONNECTION_ERROR) :
            return "No se puede establecer la conexión con el servidor de máquinas virtuales"   
        elif (code == ERROR_DESC_T.CLSRVR_VMSRVR_CONNECTION_LOST) :
            return "Se ha perdido la conexión con el servidor de máquinas virtuales"   
        elif (code == ERROR_DESC_T.CLSRVR_DOMAIN_NOT_REGISTERED) :
            return "La máquina virtual no está registrada"   
        elif (code == ERROR_DESC_T.CLSRVR_ACTIVE_VMSRVR) :
            return "El servidor de máquinas virtuales está activo"   
        elif (code == ERROR_DESC_T.CLSRVR_VMSRVR_IDS_IN_USE) :
            return "La IP o el puerto especificados están en uso"   
        elif (code == ERROR_DESC_T.CLSRVR_AUTOD_ERROR) :
            return "El despliegue automático ha fallado en algunos servidores de máquinas virtuales"   
        elif (code == ERROR_DESC_T.CLSRVR_VM_BOOT_TIMEOUT) :
            return "La máquina virtual no se puede arrancar (timeout)"   
        elif (code == ERROR_DESC_T.CLSRVR_IMAGE_NOT_AVAILABLE) :
            return "La máquina virtual no se puede arrancar (no hay servidores disponibles)"   
        elif (code == ERROR_DESC_T.CLSRVR_NO_EDITION_SRVRS) :
            return "No hay servidores en los que editar la imagen"   
        elif (code == ERROR_DESC_T.CLSRVR_NO_CANDIDATE_SRVRS) :
            return "No hay servidores en los que desplegar la imagen"         
        elif (code == ERROR_DESC_T.CLSRVR_EDITION_VMSRVRS_UNDER_FULL_LOAD) :
            return "Los servidores de edición no admiten más peticiones"       
        elif (code == ERROR_DESC_T.CLSRVR_EDITION_VMSRVRS_UNDER_FULL_LOAD) :
            return "Los servidores de máquinas virtuales no admiten más peticiones"