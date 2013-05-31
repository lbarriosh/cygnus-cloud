# -*- coding: utf8 -*
'''
Created on 14/01/2013

@author: saguma
'''

from ccutils.configurationFiles.configParametersManager import ConfigParametersManager

class VMServerConstantsManager(ConfigParametersManager):
    
    def __init__(self):
        ConfigParametersManager.__init__(self)

    def _specializeDataStructure(self):
        self._data["createVirtualNetworkAsRoot"] = self._data["createVirtualNetworkAsRoot"] == "Yes" or self._data["createVirtualNetworkAsRoot"] == "yes"
        self._data["listenningPort"] = int(self._data["listenningPort"])
        self._data["passwordLength"] = int(self._data["passwordLength"])
        self._data["FTPTimeout"] = int(self._data["FTPTimeout"])            