# -*- coding: utf8 -*


from ccutils.configurationFiles.constantsManager import ConstantsManager

class ClusterServerConstantsManager(ConstantsManager):
    
    def __init__(self):
        ConstantsManager.__init__(self)
    
    def _specializeDataStructure(self):
        self._data["listenningPort"] = int(self._data["listenningPort"])
        self._data["vmBootTimeout"] = int(self._data["vmBootTimeout"])  
        self._data["statusUpdateInterval"] = int(self._data["statusUpdateInterval"])
        if (self._data.has_key("vCPUsWeight")) :
            self._data["vCPUsWeight"] = float(self._data["vCPUsWeight"])
            self._data["vCPUsExcessThreshold"] = float(self._data["vCPUsExcessThreshold"])       
            self._data["ramWeight"] = float(self._data["ramWeight"])        
            self._data["storageSpaceWeight"] = float(self._data["storageSpaceWeight"])        
            self._data["temporarySpaceWeight"] = float(self._data["temporarySpaceWeight"])      
            self._data["imageRepositoryPort"] = int(self._data["imageRepositoryPort"])    
            self._data["imageCompressionRatio"] = float(self._data["imageCompressionRatio"])  
            self._data["dataImageExpectedSize"] = float(self._data["dataImageExpectedSize"])              