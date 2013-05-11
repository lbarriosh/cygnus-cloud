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