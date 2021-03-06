# -*- coding: UTF8 -*-
'''
Lector de la base de datos de estado

@author: Luis Barrios Hernández
@version: 2.5
'''

from database.utils.connector import BasicDatabaseConnector

class SystemStatusDatabaseReader(BasicDatabaseConnector):
    """
    Inicializa el estado del lector
    Argumentos:
        sqlUser: usuario SQL a utilizaqr
        sqlPassword: contraseña de ese usuario
        databaseName: nombre de la base de datos de estado
    """
    def __init__(self, sqlUser, sqlPassword, databaseName):
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPassword, databaseName)
                  
    def getVMServersData(self):
        """
        Devuelve los datos básicos de todos los servidores de máquinas virtuales
        Argumentos:
            Ninguno
        Returns: una lista de diccionarios, cada uno de los cuales contiene los datos
        de un servidor de máquinas virtuales
        """
        command = "SELECT * FROM VirtualMachineServer;"
        results = self._executeQuery(command, False)
        retrievedData = []
        for row in results :
            d = dict()
            d["VMServerName"] = row[0]
            d["VMServerStatus"] = row[1]
            d["VMServerIP"] = row[2]
            d["VMServerListenningPort"] = int(row[3])
            d["IsVanillaServer"] = int(row[4]) == 1
            retrievedData.append(d)
        return retrievedData
    
    def getVMDistributionData(self):
        """
        Devuelve la distribución de todas las máquinas virtuales
        Argumentos:
            Ninguno
        Devuelve: 
            una lista de diccionarios. Cada uno contiene una ubicación de una
            imagen.
        """
        command = "SELECT * FROM VirtualMachineDistribution;"
        results = self._executeQuery(command, False)
        retrievedData = []
        for row in results :
            d = dict()
            d["VMServerName"] = row[0]
            d["VMID"] = int(row[1])
            retrievedData.append(d)
        return retrievedData 
    
    def getActiveVMsData(self, ownerID):
        """
        Devuelve los datos de las máquinas virtuales activas
        Argumentos:
            ownerID: identificador del propietario de las máquinas. Si es None, se devolverán
            los datos de todas las máquinas virtuales.
        Devuelve: 
            una lista de diccionarios. Cada uno contiene los datos de una máquina
        """
        if (ownerID == None) :
            command = "SELECT * FROM ActiveVirtualMachines;"
        else :
            command = "SELECT * FROM ActiveVirtualMachines WHERE ownerID = {0};".format(ownerID)
            
        results = self._executeQuery(command, False)
        retrievedData = []
        for row in results :
            d = dict()
            d["VMServerName"] = row[0]
            d["DomainUID"] = row[1]
            d["UserID"] = row[2]
            d["VMID"] = int(row[3])            
            d["VMName"] = row[4]
            d["VNCPort"] = int(row[5])
            d["VNCPassword"] = row[6]
            retrievedData.append(d)
        return retrievedData 