# -*- coding: utf8 -*
'''
Created on 14/01/2013

@author: saguma
'''

from ccutils.configurationFiles.configurationFileReader import ConfigurationFileReader

class ConstantsManager(object):
    def __init__(self):
        self._data = {}

    def parseConfigurationFile(self, configurationFilePath):
        try :
            reader = ConfigurationFileReader()
            reader.parseConfigurationFile(configurationFilePath)
            self._data = reader.getParsedData()
            if self._data.has_key("uninitializedFile") :
                raise Exception("Uninitialized configuration file")
            if (self._data == {}) :
                raise Exception("File not found")    
                
            self._specializeDataStructure()          
            
        except Exception as e:
            self._data = {}
            raise Exception("Invalid configuration file: " + e.message)
        
    def _specializeDataStructure(self):
        raise NotImplementedError
        
    def getConstant(self, label):
        return self._data[label]