# -*- coding: utf8 -*


from ccutils.configurationFiles.constantsManager import ConstantsManager

class ClusterServerConstantsManager(ConstantsManager):
    
    def __init__(self):
        ConstantsManager.__init__(self)
    
    def _specializeDataStructure(self):
        self._data["listenningPort"] = int(self._data["listenningPort"])
        self._data["vmBootTimeout"] = int(self._data["vmBootTimeout"])  
        self._data["statusUpdateInterval"] = int(self._data["statusUpdateInterval"])