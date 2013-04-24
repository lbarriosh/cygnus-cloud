#coding=utf-8

from ccutils.configurationFiles.constantsManager import ConstantsManager

"""
Parser del fichero de configuración del repositorio
"""
class ImageRepositoryConstantsManager(ConstantsManager):
    
    """
    Inicializa el estado del parser
    Argumentos:
        Ninguno
    """
    def __init__(self):
        ConstantsManager.__init__(self)

    """
    Convierte algunos elementos de la estructrura de datos
    a tipos más específicos.
    Argumentos:
        Ninguno
    Devuelve:
        Nada
    """
    def _specializeDataStructure(self):
        self._data["commandsPort"] = int(self._data["commandsPort"])
        self._data["FTPPort"] = int(self._data["FTPPort"])
        self._data["maxConnections"] = int(self._data["maxConnections"])
        self._data["maxConnectionsPerIP"] = int(self._data["maxConnectionsPerIP"])
        self._data["uploadBandwidthRatio"] = float(self._data["uploadBandwidthRatio"])
        self._data["downloadBandwidthRatio"] = float(self._data["downloadBandwidthRatio"])
        self._data["FTPPasswordLength"] = int(self._data["FTPPasswordLength"])