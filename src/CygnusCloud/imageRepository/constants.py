#coding=utf-8

from ccutils.configurationFiles.constantsManager import ConstantsManager

class ImageRepositoryConstantsManager(ConstantsManager):
    
    def __init__(self):
        ConstantsManager.__init__(self)

    def _specializeDataStructure(self):
        self._data["commandsPort"] = int(self._data["commandsPort"])
        self._data["dataPort"] = int(self._data["dataPort"])
        self._data["maxUploadSlots"] = int(self._data["maxUploadSlots"])
        self._data["maxDownloadSlots"] = int(self._data["maxDownloadSlots"])