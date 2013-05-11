# -*- coding: utf8 -*
'''
Created on May 11, 2013

@author: luis
'''
from codeTranslator import CodeTranslator

from clusterServer.database.clusterServerDB import SERVER_STATE_T, IMAGE_STATE_T

class SpanishCodeTranslator(CodeTranslator):
    def processVMServerSegment(self, data):
        result = []
        for tup in data :
            tmp = list(tup)
            if (tmp[1] == SERVER_STATE_T.BOOTING) :
                tmp[1] = "Arrancando"
            elif (tmp[1] == SERVER_STATE_T.READY) :
                tmp[1] = "Listo"
            elif (tmp[1] == SERVER_STATE_T.SHUT_DOWN):
                tmp[1] = "Apagado"
            elif (tmp[1] == SERVER_STATE_T.RECONNECTING):
                tmp[1] = "Reestableciendo conexión"
            else :
                tmp[1] = "Apagado - Fallo de conexión"            
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