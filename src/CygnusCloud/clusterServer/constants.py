# -*- coding: utf8 -*


from ccutils.configurationFiles.constantManager import ConstantsManager

class ClusterServerConstantsManager(ConstantsManager):
    def _specializeDataStructure(self):
        self._data["listenningPort"] = int(self._data["listenningPort"])
        self._data["vmBootTimeout"] = int(self._data["vmBootTimeout"])  