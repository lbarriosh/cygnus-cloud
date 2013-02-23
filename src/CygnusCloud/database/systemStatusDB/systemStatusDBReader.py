# -*- coding: UTF8 -*-
'''
Web status database reader definitions

@author: Luis Barrios Hernández
@version: 2.1
'''

from database.utils.connector import BasicDatabaseConnector

class SystemStatusDatabaseReader(BasicDatabaseConnector):
    """
    Initializes the reader's state
    Args:
        sqlUser: the SQL user to use
        sqlPassword: the SQL user's password
        databaseName: the database's name
    """
    def __init__(self, sqlUser, sqlPassword, databaseName):
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPassword, databaseName)
                  
    def getVMServersData(self):
        """
        Returns the virtual machine server's basic data.
        Args:
            None
        Returns: a list of dictionaries with the keys VMServerName, VMServerStatus, VMServerIP,
            VMServerListenningPort and their corresponding values.
        """
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
        """
        Returns the image (a.k.a. available virtual machines) distribution data.
        Args:
            None
        Returns: a list of dictionaries with the keys VMServerName, VMID and the corresponding values
        """
        command = "SELECT * FROM VirtualMachineDistribution;"
        results = self._executeQuery(command, False)
        retrievedData = []
        for row in results :
            d = dict()
            d["VMServerName"] = row[0]
            d["VMID"] = row[1]
            retrievedData.append(d)
        return retrievedData 
    
    def getActiveVMsData(self):
        """
        Returns the active virtual machines' data.
        Args:
            None
        Returns: a list of dictionaries with the keys VMServerName, UserID, VMID, VMName, VNCPort
            and VNCPassword with their corresponding values.
        """
        command = "SELECT * FROM ActiveVirtualMachines;"
        results = self._executeQuery(command, False)
        retrievedData = []
        for row in results :
            d = dict()
            d["VMServerName"] = row[0]
            d["UserID"] = row[1]
            d["VMID"] = row[2]
            d["VMName"] = row[3]
            d["VNCPort"] = row[4]
            d["VNCPassword"] = row[5]
            retrievedData.append(d)
        return retrievedData 