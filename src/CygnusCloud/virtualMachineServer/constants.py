# -*- coding: utf8 -*
'''
Created on 14/01/2013

@author: saguma
'''

from ccutils.configurationFiles.configurationFileReader import ConfigurationFileReader

class ConstantsManager(object):
    def __init__(self):
        self.__data = {}

    def parseConfigurationFile(self, configurationFilePath):
        try :
            reader = ConfigurationFileReader()
            reader.parseConfigurationFile(configurationFilePath)
            self.__data = reader.getParsedData()
            if self.__data.has_key("uninitializedFile") :
                raise Exception("Uninitialized configuration file")
            if (self.__data == {}) :
                raise Exception("File not found")    
                
            self.__data["createVirtualNetworkAsRoot"] = self.__data["createVirtualNetworkAsRoot"] == "Yes" or self.__data["createVirtualNetworkAsRoot"] == "yes"
            self.__data["listenningPort"] = int(self.__data["listenningPort"])
            self.__data["passwordLength"] = int(self.__data["passwordLength"])            
            
        except Exception as e:
            self.__data = {}
            raise Exception("Invalid configuration file: " + e.message)
        
    def getConstant(self, label):
        return self.__data[label]