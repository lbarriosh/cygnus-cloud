# -*- coding: utf8 -*


from ccutils.configurationFiles.constantsManager import ConstantsManager

class WebServerEndpointConstantsManager(ConstantsManager):
    
    def __init__(self):
        ConstantsManager.__init__(self)
    
    def _specializeDataStructure(self):
        self._data["clusterServerListenningPort"] = int(self._data["clusterServerListenningPort"])
        self._data["statusDBUpdateInterval"] = int(self._data["statusDBUpdateInterval"])  