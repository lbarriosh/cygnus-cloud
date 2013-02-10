# -*- coding: UTF8 -*-
'''
Web status database reader definitions

@author: Luis Barrios Hernández
@version: 2.0
'''

from database.utils.connector import BasicDatabaseConnector

class SystemStatusDatabaseReader(BasicDatabaseConnector):
    def __init__(self, sqlUser, sqlPassword, databaseName):
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPassword, databaseName)
                  
    def getVMServersData(self):
        command = "SELECT * FROM VirtualMachineServer;"
        results = self._executeQuery(command, False)
        retrievedData = []
        for row in results :
            d = dict()
            d["VMServerName"] = row[0]
            d["VMServerStatus"] = row[1]
            d["VMServerIP"] = row[2]
            d["VMServerListenningPort"] = row[3]
            retrievedData.append(d)
        return retrievedData
    
    def getVMDistributionData(self):
        command = "SELECT * FROM VirtualMachineDistribution;"
        results = self._executeQuery(command, False)
        retrievedData = []
        for row in results :
            d = dict()
            d["VMServerName"] = row[0]
            d["VMID"] = row[1]
            retrievedData.append(d)
        return retrievedData 