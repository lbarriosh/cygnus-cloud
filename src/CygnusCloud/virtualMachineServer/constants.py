# -*- coding: utf8 -*
'''
Created on 14/01/2013

@author: saguma
'''

from ccutils.configurationFiles.constantManager import ConstantsManager

class VMServerConstantsManager(ConstantsManager):
    def __init__(self):
        self._data = {}

    def _specializeDataStructure(self):
        self._data["listenningPort"] = int(self._data["listenningPort"])
        self._data["vmBootTimeout"] = int(self._data["vmBootTimeout"])  