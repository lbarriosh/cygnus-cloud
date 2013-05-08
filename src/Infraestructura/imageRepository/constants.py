#coding=utf-8

from ccutils.configurationFiles.constantsManager import ConstantsManager

class ImageRepositoryConstantsManager(ConstantsManager):
    """
    Parser del fichero de configuración del repositorio
    """
    
    def __init__(self):
        """
        Inicializa el estado del parser
        Argumentos:
            Ninguno
        """
        ConstantsManager.__init__(self)
    
    def _specializeDataStructure(self):
        """
        Convierte algunos elementos de la estructrura de datos
        a tipos más específicos.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        self._data["commandsPort"] = int(self._data["commandsPort"])
        self._data["FTPPort"] = int(self._data["FTPPort"])
        self._data["maxConnections"] = int(self._data["maxConnections"])
        self._data["maxConnectionsPerIP"] = int(self._data["maxConnectionsPerIP"])
        self._data["uploadBandwidthRatio"] = float(self._data["uploadBandwidthRatio"])
        self._data["downloadBandwidthRatio"] = float(self._data["downloadBandwidthRatio"])
        self._data["FTPPasswordLength"] = int(self._data["FTPPasswordLength"])