# -*- coding: utf8 -*


from ccutils.configurationFiles.constantsManager import ConstantsManager

class ClusterEndpointConstantsManager(ConstantsManager):
    
    def __init__(self):
        ConstantsManager.__init__(self)
    
    def _specializeDataStructure(self):
        self._data["clusterServerListenningPort"] = int(self._data["clusterServerListenningPort"])
        self._data["statusDBUpdateInterval"] = int(self._data["statusDBUpdateInterval"])  
        self._data["commandTimeout"] = float(self._data["commandTimeout"])
        self._data["commandTimeoutCheckInterval"] = float(self._data["commandTimeoutCheckInterval"])
        self._data["minCommandInterval"] = float(self._data["minCommandInterval"]) 