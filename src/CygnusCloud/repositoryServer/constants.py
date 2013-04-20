#coding=utf-8

from ccutils.configurationFiles.constantsManager import ConstantsManager

class RepositoryConstantsManager(ConstantsManager):
    
    def __init__(self):
        ConstantsManager.__init__(self)

    def _specializeDataStructure(self):
        self._data["listenningPort"] = int(self._data["listenningPort"])