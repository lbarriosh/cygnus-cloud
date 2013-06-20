# -*- coding: UTF8 -*-
'''
Lector de la base de datos de estado

@author: Luis Barrios Hernández
@version: 4.0
'''
from editionState_t import EDITION_STATE_T
from ccutils.databases.connector import BasicDBConnector

class MinimalClusterEndpointDBConnector(BasicDBConnector):
    """
    Inicializa el estado del lector
    Argumentos:
        sqlUser: usuario SQL a utilizar
        sqlPassword: contraseña de ese usuario
        databaseName: nombre de la base de datos de estado
    """
    def __init__(self, sqlUser, sqlPassword, databaseName):
        BasicDBConnector.__init__(self, sqlUser, sqlPassword, databaseName)
        
    def getImageID(self, temporaryID):
        query = "SELECT imageID FROM EditedImage WHERE temporaryID = '{0}';".format(temporaryID)
        return self._executeQuery(query, True)        
        
    def getActiveVMsData(self, ownerID, show_edited):
        """
        Devuelve los datos de las máquinas virtuales activas
        Argumentos:
            ownerID: identificador del propietario de las máquinas. Si es None, se devolverán
            los datos de todas las máquinas virtuales.
        Devuelve: 
            una lista de diccionarios. Cada uno contiene los datos de una máquina
        """
        if (ownerID == None):            
            if (show_edited) :
                modifier = ""
            else :
                modifier = "NOT"
            command = "SELECT * FROM ActiveVirtualMachines ActVMs WHERE {0} EXISTS \
                    (SELECT * FROM EditedImage WHERE ActVMs.domainUID = EditedImage.temporaryID);".format(modifier)
        else :
            if (show_edited) :
                modifier = ""
            else :
                modifier = "NOT"
            command = "SELECT * FROM ActiveVirtualMachines ActVMs WHERE ownerID = {0} AND {1} EXISTS \
                    (SELECT * FROM EditedImage WHERE ActVMs.domainUID = EditedImage.temporaryID);".format(ownerID, modifier)
            
        results = self._executeQuery(command, False)
        if (results == None) :
            return []
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
        if (results == None) :
            return []
        retrievedData = []
        for row in results :
            d = dict()
            d["VMServerName"] = row[0]
            d["ImageID"] = int(row[1])
            d["CopyStatus"] = row[2]
            retrievedData.append(d)
        return retrievedData 
    
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
        if (results == None) :
            return []
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
    
    def getImageData(self, imageID):
        
        if (isinstance(imageID, int)) :
            query = "SELECT name, description, vanillaImageFamilyID,\
                osFamily, osVariant, isBaseImage, isBootable, imageID FROM Image WHERE imageID = {0}".format(imageID)
            result = self._executeQuery(query, True)
            if (result == None) : 
                query = "SELECT name, description, vanillaImageFamilyID,\
                osFamily, osVariant, imageID FROM EditedImage WHERE imageID = {0}".format(imageID)
                result = self._executeQuery(query, True)
                if (result == None) :
                    return None
            d = dict()
            d["ImageName"] = str(result[0])
            d["ImageDescription"] = str(result[1])
            d["VanillaImageFamilyID"] = int(result[2])
            d["OSFamily"] = int(result[3])
            d["OSVariant"] = int(result[4])
            if (len(result) == 8) :
                d["IsBaseImage"] = bool(result[7])
            else:
                d["IsBaseImage"] = False
            d["IsBootable"] = result[5] == 1
            d["State"] = EDITION_STATE_T.NOT_EDITED
            d["ImageID"] = int(result[6])
            d["EditedImage"] = False
        else :
            query = "SELECT name, description, vanillaImageFamilyID,\
                osFamily, osVariant, ownerID, imageID, state, editedImage FROM EditedImage WHERE temporaryID = '{0}'".format(imageID)
            result = self._executeQuery(query, True)
            d = dict()
            d["ImageName"] = str(result[0])
            d["ImageDescription"] = str(result[1])
            d["VanillaImageFamilyID"] = int(result[2])
            d["OSFamily"] = int(result[3])
            d["OSVariant"] = int(result[4])
            d["IsBaseImage"] = False
            d["IsBootable"] = False
            d["State"] = int(result[7])
            d["OwnerID"] = int(result[5])
            d["ImageID"] = int(result[6])
            d["EditedImage"] = bool(result[1])
        return d       
    
    def getBootableImagesData(self, imageIDs):
        query = "SELECT imageID, name, description, vanillaImageFamilyID,\
                osFamily, osVariant FROM Image WHERE isBootable = 1"
        if (imageIDs != []) :
            query += " AND ("
            i = 0
            for imageID in imageIDs :
                query += "imageID = {0} ".format(imageID)
                if (i != len(imageIDs) - 1) :
                    query += " OR "
                i += 1
            query += ");"
        result = self._executeQuery(query, False)        
        if (result == None) :
            return []
        else :
            rows = []
            for row in result :
                rows.append({"ImageID": row[0], "ImageName" : str(row[1]), "ImageDescription" : str(row[2]),
                             "VanillaImageFamilyID" : row[3], "OSFamily" : row[4], "OSVariant" : row[5]})
        return rows
    
    def getBaseImagesData(self):
        query = "SELECT imageID, name, description, vanillaImageFamilyID,\
                osFamily, osVariant FROM Image WHERE isBaseImage = 1;"
        result = self._executeQuery(query, False)
        if (result == None) :
            return []
        else :
            rows = 0
            rows = []
            for row in result :
                rows.append({"ImageID": row[0], "ImageName" : str(row[1]), "ImageDescription" : str(row[2]),
                             "VanillaImageFamilyID" : row[3], "OSFamily" : row[4], "OSVariant" : row[5]})
            return rows
        
    def getEditedImageIDs(self, userID=None):
        if (userID != None) :
            query = "SELECT temporaryID FROM EditedImage WHERE ownerID = {0};".format(userID)
        else :
            query = "SELECT temporaryID FROM EditedImage;"
        result = self._executeQuery(query, False)
        rows = []
        if (result != None) :
            for row in result :
                rows.append(str(row))
        return rows
    
    def getVanillaImageFamilyID(self, imageID):
        if (isinstance(imageID, int)) :
            query = "SELECT vanillaImageFamilyID FROM Image WHERE imageID = {0}".format(imageID)
            result = self._executeQuery(query, True)
            if (result == None) :
                query = "SELECT vanillaImageFamilyID FROM EditedImage WHERE imageID = {0}".format(imageID)
                result = self._executeQuery(query, True)
            return result
        else :
            query = "SELECT vanillaImageFamilyID FROM EditedImage WHERE temporaryID = '{0}'".format(imageID)
            return self._executeQuery(query, True)
        
    def getVanillaImageFamilyData(self, vanillaImageFamilyID):
        query = "SELECT familyName, ramSize, vCPUs, osDiskSize, dataDiskSize FROM VanillaImageFamily WHERE familyID = {0}".format(vanillaImageFamilyID)
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            return {"Name" : str(result[0]), "RAMSize" : result[1], "VCPUs": result[2], "OSDiskSize" : result[3], "DataDiskSize" : result[4]}
        
    def getMaxVanillaImageFamilyData(self):
        query = "SELECT MAX(ramSize), MAX(vCPUs), MAX(osDiskSize), MAX(dataDiskSize) FROM VanillaImageFamily;"
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            return {"RAMSize" : result[0], "VCPUs": result[1], "OSDiskSize" : result[2], "DataDiskSize" : result[3]}
        
    def getImageRepositoryStatus(self):
        query = "SELECT freeDiskSpace, availableDiskSpace, repositoryStatus FROM ImageRepositoryStatus;"
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            d = dict()
            d["FreeDiskSpace"] = result[0]
            d["AvailableDiskSpace"] = result[1]
            d["RepositoryStatus"] = str(result[2])
            return d
        
    def getVirtualMachineServerStatus(self, serverName):
        query = "SELECT hosts, ramInUse, ramSize, freeStorageSpace, availableStorageSpace, \
            freeTemporarySpace, availableTemporarySpace, activeVCPUs, physicalCPUs\
            FROM VirtualMachineServerStatus WHERE serverName = '{0}';".format(serverName)
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            d = dict()
            d["ActiveHosts"] = int(result[0])
            d["RAMInUse"] = int(result[1])
            d["RAMSize"] = int(result[2])
            d["FreeStorageSpace"] = int(result[3])
            d["AvailableStorageSpace"] = int(result[4])
            d["FreeTemporarySpace"] = int(result[5])
            d["AvailableTemporarySpace"] = int(result[6])
            d["ActiveVCPUs"] = int(result[7])
            d["PhysicalCPUs"] = int(result[8])
            return d  
        
    def getOSTypes(self):
        query = "SELECT familyID, familyName FROM OSFamily;"
        results = self._executeQuery(query, False)
        if (results == None) :
            return []
        retrievedData = []
        for row in results :
            d = dict()
            d["FamilyID"] = row[0]
            d["FamilyName"] = row[1]
            retrievedData.append(d)
        return retrievedData
        
    def getOSTypeVariants(self,familyID):
        query = "SELECT variantID, variantName FROM OSVariant WHERE familyID = '{0}';".format(familyID)
        results = self._executeQuery(query, False)
        if (results == None) :
            return []
        retrievedData = []
        for row in results :
            d = dict()
            d["VariantID"] = row[0]
            d["VariantName"] = row[1]
            retrievedData.append(d)
        return retrievedData    