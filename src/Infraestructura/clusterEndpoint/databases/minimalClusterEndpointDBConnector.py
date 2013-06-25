# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: MinimalClusterEndpointDBConnector.py    
    Version: 5.0
    Description: minimal cluster endpoint database connector 
    
    Copyright 2012-13 Luis Barrios Hernández, Adrián Fernández Hernández,
        Samuel Guayerbas Martín
        
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''
from editionState_t import EDITION_STATE_T
from ccutils.databases.connector import BasicDBConnector

class MinimalClusterEndpointDBConnector(BasicDBConnector):
    """
    Minimal cluster endpoint database connector
    """
    
    def __init__(self, sqlUser, sqlPassword, databaseName):
        """
        Initializes the connector's state
        Args:
            sqlUser: the MySQL user to use
            sqlPassword: the MySQL password to use
            databaseName: a MySQL database name.
        """
        BasicDBConnector.__init__(self, sqlUser, sqlPassword, databaseName)
        
    def getImageID(self, temporaryID):
        """
        Returns the image id associated with a temporary ID
        Args:
            temporaryID: a temporary ID
        Returns:
            the image id associated with the given image ID
        """
        query = "SELECT imageID FROM EditedImage WHERE temporaryID = '{0}';".format(temporaryID)
        return self._executeQuery(query, True)        
        
    def getActiveVMsVNCData(self, ownerID, show_edited):
        """
        Returns the active virtual machine's data
        Argumentos:
            ownerID: the virtual machines' owner. If it's None, all the active virtual machines' VNC data
            will be returned
            show_edited: if it's True, the edition virtual machines data will also be returned.
        Returns:
            a list of dictionaries. Each one contains an active virtual machine's VNC data
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
    
    def getImageCopiesDistributionData(self):
        """
        Returns all the image copies distribution.
        Args:
            None
        Returns:
            a list of dictionaries. Each one contains an image location's data.
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
    
    def getVMServersConfiguration(self):
        """
        Returns all the virtual machine servers configuration
        Args:
            None
        Returns:
            a list of dictionaries. Each one contains a virtual machine server's configuration.
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
        """
        Returns an image's data
        Args:
            imageID: a permanent or a temporary image ID
        Returns:
            a dictionary containing the image's data
        """
        lookAtEditedImage = True
        
        if (isinstance(imageID, int)) :
            query = "SELECT name, description, vanillaImageFamilyID,\
                osFamily, osVariant, isBaseImage, isBootable, imageID FROM Image WHERE imageID = {0}".format(imageID)
            result = self._executeQuery(query, True)
            if (result != None) :
                lookAtEditedImage = False
                d = dict()
                d["ImageName"] = str(result[0])
                d["ImageDescription"] = str(result[1])
                d["VanillaImageFamilyID"] = int(result[2])
                d["OSFamily"] = int(result[3])
                d["OSVariant"] = int(result[4])
                d["IsBaseImage"] = bool(result[5])
                d["IsBootable"] = bool(result[6])
                d["ImageID"] = int(result[7])                
                d["EditedImage"] = False                
                d["State"] = EDITION_STATE_T.NOT_EDITED
            else :
                query = "SELECT temporaryID FROM EditedImage WHERE imageID = {0}".format(imageID)
                imageID = self._executeQuery(query, True)
            
        if (lookAtEditedImage) :
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
            d["EditedImage"] = bool(result[8])
        
        return d       
    
    def getBootableImagesData(self, imageIDs):
        """
        Returns the bootable image data
        Args:
            imageID: a list of image identifiers. If it's not empty, it will be used
            to filter the query results.
        Returns:
            A list of dictionaries. Each one contains a bootable image's data.
        """
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
        """
        Returns the base images data
        Args:
            None
        Returns: 
             A list of dictionaries. Each one contains a base image's data.
        """
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
        """
        Returns the edited images temporary IDs
        Args:
            userID: a user ID. If it's none, all the edited images' IDs will be returned
        Returns:
            a list containing the edited images' temporary IDs.
        """
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
    
    def getVMFamilyID(self, imageID):
        """
        Returns the virtual machine family ID associated with an image.
        Args:
            imageID: an image ID
        Returns:
            the virtual machine family ID associated with the given image.
        """
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
        
    def getVMFamilyData(self, vmFamilyID):
        """
        Returns a virtual machine family data
        Args:
            vmFamilyID: a virtual machine family ID
        Returns:
            A dictionary containing the virtual machine family's data
        """
        query = "SELECT familyName, ramSize, vCPUs, osDiskSize, dataDiskSize FROM VanillaImageFamily WHERE familyID = {0}".format(vmFamilyID)
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            return {"Name" : str(result[0]), "RAMSize" : result[1], "VCPUs": result[2], "OSDiskSize" : result[3], "DataDiskSize" : result[4]}
        
    def getMaxVMFamilyData(self):
        """
        Returns the most powerful virtual machine family data
        Args:
            None
        Returns:
            A dictionary containing the most powerful virtual machine family data
        """
        query = "SELECT MAX(ramSize), MAX(vCPUs), MAX(osDiskSize), MAX(dataDiskSize) FROM VanillaImageFamily;"
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            return {"RAMSize" : result[0], "VCPUs": result[1], "OSDiskSize" : result[2], "DataDiskSize" : result[3]}
        
    def getImageRepositoryStatus(self):
        """
        Returns the image repository current status
        Args:
            None
        Returns:
            A dictionary containing the image repository current status
        """
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
        """
        Returns a virtual machine server's status
        Args:
            A virtual machine server's name
        Returns:
            a dictionary containing the virtual machine server's status
        """
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
        """
        Returns the registered OS types
        Args:
            None
        Returns:
            a list of dictionaries. Each one contains one of the registered OS types data.
        """
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
        """
        Returns the registered OS variants
        Args:
            None
        Returns:
            a list of dictionaries. Each one contains one of the registered OS variantas data.
        """
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