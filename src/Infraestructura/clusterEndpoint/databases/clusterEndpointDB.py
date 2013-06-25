# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: clusterEndpointDB.py    
    Version: 5.0
    Description: full cluster endpoint database connector 
    
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

from clusterEndpoint.databases.minimalClusterEndpointDBConnector import MinimalClusterEndpointDBConnector

class ClusterEndpointDBConnector(MinimalClusterEndpointDBConnector):
    """
    Initializes the connector's state
    Args:
        sqlUser: the MySQL user to use
        sqlPassword: the MySQL password to use
        databaseName: a MySQL database name.
    """
    def __init__(self, sqlUser, sqlPassword, databaseName):
        MinimalClusterEndpointDBConnector.__init__(self, sqlUser, sqlPassword, databaseName)
        self.__vmServerSegmentsData = []
        self.__vmServerSegments = 0
        self.__vmServerResourceUsageData = []
        self.__vmServerResourceUsageSegments = 0
        self.__imageDistributionSegmentsData = []
        self.__imageDistributionSegments = 0
        self.__activeVMSegmentsData = dict()
        self.__activeVMSegments = dict()
    
    def processVMServerResourceUsageSegment(self, segmentNumber, segmentCount, data):
        """
        Processes a virtual machine server resource usage segment
        Args:
            segmentNumber: the segment's position in the sequence
            segmentCount: the number of segments in the sequence
            data: the segment's data
        Returns:
            Nothing
        """
        if (data != []) :
            self.__vmServerResourceUsageData += data
            self.__vmServerResourceUsageSegments += 1
            
        if (self.__vmServerResourceUsageSegments == segmentCount) :
            receivedData = ClusterEndpointDBConnector.__getVMServersDictionary(self.__vmServerResourceUsageData)
            registeredIDs = self.__getKnownVMServerIDs("VirtualMachineServerStatus")
            
            if (registeredIDs != None) :
                for ID in registeredIDs :
                    if not (receivedData.has_key(ID)) :
                        self.__deleteVMServerStatusData(ID)
                        
            inserts = []
            for ID in receivedData.keys() :
                if (registeredIDs != None and ID in registeredIDs) :
                    self.__updateVMServerStatusData(receivedData[ID])
                else :
                    inserts.append(receivedData[ID])
                    
            if (inserts != []) :
                self.__insertVMServerStatusData(inserts)
            self.__vmServerResourceUsageData = []
            self.__vmServerResourceUsageSegments = 0
            
    def __insertVMServerStatusData(self, tupleList):
        update = "INSERT INTO VirtualMachineServerStatus VALUES {0};"\
            .format(ClusterEndpointDBConnector.__convertTuplesToSQLStr(tupleList))
        self._executeUpdate(update)
            
    def __updateVMServerStatusData(self, receivedData):
        update = "UPDATE VirtualMachineServerStatus SET hosts = {0}, ramInUse = {1}, ramSize = {2},\
            freeStorageSpace = {3}, availableStorageSpace = {4}, freeTemporarySpace = {5}, availableTemporarySpace = {6},\
            activeVCPUs = {7}, physicalCPUs = {8} WHERE serverName = '{9}';".format(receivedData[1], receivedData[2], receivedData[3],
                                                           receivedData[4], receivedData[5], receivedData[6], receivedData[7],
                                                           receivedData[8], receivedData[9], receivedData[0])
        self._executeUpdate(update)
            
    def __deleteVMServerStatusData(self, serverID):
        update = "DELETE FROM VirtualMachineServerStatus WHERE serverID = '{0}';".format(serverID)
        self._executeUpdate(update)
    
    def processVMServerSegment(self, segmentNumber, segmentCount, data):
        """
        Processes a virtual machine server configuration segment
        Args:
            segmentNumber: the segment's position in the sequence
            segmentCount: the number of segments in the sequence
            data: the segment's data
        Returns:
            Nothing
        """
        if (data != []) :
            self.__vmServerSegmentsData += data
            self.__vmServerSegments += 1
            
        if (self.__vmServerSegments == segmentCount) :
            receivedData = ClusterEndpointDBConnector.__getVMServersDictionary(self.__vmServerSegmentsData)
            registeredIDs = self.__getKnownVMServerIDs()
            
            if (registeredIDs != None) :
                for ID in registeredIDs :
                    if not (receivedData.has_key(ID)) :
                        self.__deleteVMServer(ID)
                        
            inserts = []
            for ID in receivedData.keys() :
                if (registeredIDs != None and ID in registeredIDs) :
                    self.__updateVMServerData(receivedData[ID])
                else :
                    inserts.append(receivedData[ID])
                    
            if (inserts != []) :
                self.__insertVMServers(inserts)
            self.__vmServerSegmentsData = [] 
            self.__vmServerSegments = 0
            
    def processImageCopiesDistributionSegment(self, segmentNumber, segmentCount, data):
        """
        Processes an image copies distribution segment
        Args:
            segmentNumber: the segment's position in the sequence
            segmentCount: the number of segments in the sequence
            data: the segment's data
        Returns:
            Nothing
        """
        if (data != []) :
            self.__imageDistributionSegmentsData.append(data)
            self.__imageDistributionSegments += 1
        if (self.__imageDistributionSegments == segmentCount) :            
            # Borrar la tabla y volver a construirla
            command = "DELETE FROM VirtualMachineDistribution;"
            self._executeUpdate(command)
            if (self.__imageDistributionSegmentsData != []) :
                command = "INSERT INTO VirtualMachineDistribution VALUES " + ClusterEndpointDBConnector.__convertSegmentsToSQLTuples(self.__imageDistributionSegmentsData)
                self.__imageDistributionSegmentsData = []   
                self.__imageDistributionSegments = 0         
                self._executeUpdate(command)
    
    def processActiveVMVNCDataSegment(self, segmentNumber, segmentCount, vmServerIP, data):
        """
        Processes an active virtual machines VNC data segment
        Args:
            segmentNumber: the segment's position in the sequence
            segmentCount: the number of segments in the sequence
            data: the segment's data
        Returns:
            Nothing
        """
        if (not self.__activeVMSegmentsData.has_key(vmServerIP)) :
            self.__activeVMSegmentsData[vmServerIP] = []
            self.__activeVMSegments[vmServerIP] = 0
        if (data != []) :
            self.__activeVMSegmentsData[vmServerIP] += data
            self.__activeVMSegments[vmServerIP] += 1
        if (self.__activeVMSegments[vmServerIP] == segmentCount) :
            
            receivedData = ClusterEndpointDBConnector.__getActiveVMsDictionary(self.__activeVMSegmentsData[vmServerIP])
            registeredIDs = self.__getActiveVMIDs()            
            
            for ID in registeredIDs :                    
                if not (receivedData.has_key(ID)) :
                    self.__deleteActiveVM(ID)
                    self.updateEditedImageState(ID, EDITION_STATE_T.TRANSFER_TO_REPOSITORY, EDITION_STATE_T.VM_ON)
                        
            inserts = []
            for ID in receivedData.keys() :             
                if (not (ID in registeredIDs)) :
                    inserts.append(receivedData[ID])
                    
            if (inserts != []) :
                self.__insertActiveVMData(self.__getVMServerName(vmServerIP), inserts)
            self.__activeVMSegmentsData[vmServerIP] = []
            self.__activeVMSegments[vmServerIP] = 0
        
    @staticmethod    
    def __getVMServersDictionary(segmentList):
        result = {}
        for segment in segmentList :
            result[segment[0]] = segment
        return result
    
    @staticmethod
    def __getActiveVMsDictionary(segmentList):
        result = {}
        for segment in segmentList :
            result[segment[0]] = segment
        return result
                
    def __getKnownVMServerIDs(self, table="VirtualMachineServer"):
        query = "SELECT serverName FROM {0};".format(table)
        result = set()
        output = self._executeQuery(query, False)
        if (output == None) :
            return None
        for t in output :
            result.add(t)
        return result
            
    def __insertVMServers(self, tupleList):
        update = "INSERT INTO VirtualMachineServer VALUES {0};"\
            .format(ClusterEndpointDBConnector.__convertTuplesToSQLStr(tupleList))
        self._executeUpdate(update)
        
    def __updateVMServerData(self, data):     
        update = "UPDATE VirtualMachineServer SET serverStatus='{1}', serverIP='{2}', serverPort={3},\
            isVanillaServer = {4} WHERE serverName='{0}'".format(data[0], data[1], data[2], data[3], data[4])
        self._executeUpdate(update)
        
    def __deleteVMServer(self, serverID):
        update = "DELETE FROM ActiveVirtualMachines WHERE serverName = '{0}';".format(serverID)
        self._executeUpdate(update)
        update = "DELETE FROM VirtualMachineServer WHERE serverName = '{0}'".format(serverID)
        self._executeUpdate(update)                
            
    def __getActiveVMIDs(self):
        query = "SELECT domainUID FROM ActiveVirtualMachines;"
        results = self._executeQuery(query)
        if (results == None) :
            return set()
        output = set()
        for row in results :
            output.add(row)
        return output
    
    def __insertActiveVMData(self, vmServerIP, data):
        update = "REPLACE ActiveVirtualMachines VALUES {0};"\
            .format(ClusterEndpointDBConnector.__convertTuplesToSQLStr(data, [vmServerIP]))
        self._executeUpdate(update)
        
    def __deleteActiveVM(self, domainUID):
        update = "DELETE FROM ActiveVirtualMachines WHERE domainUID = '{0}';"\
            .format(domainUID)
        self._executeUpdate(update)
            
    def __getVMServerName(self, serverIP):
        query = "SELECT serverName FROM VirtualMachineServer WHERE serverIP = '" + serverIP + "';"
        result = self._executeQuery(query, True)
        return str(result)
                        
    @staticmethod
    def __convertTuplesToSQLStr(tupleList, dataToAdd = []):
        isFirstSegment = True
        command = ""
        for segmentTuple in tupleList :
            if (isFirstSegment) :
                isFirstSegment = False
            else :
                command += ", "
            segmentTuple_list = dataToAdd + list(segmentTuple)
            command += str(tuple(segmentTuple_list))
        return command    
    
    @staticmethod
    def __convertSegmentsToSQLTuples(segmentList):
        isFirstSegment = True
        command = ""
        for segment in segmentList :
            for segmentTuple in segment :
                if (isFirstSegment) :
                    isFirstSegment = False
                else :
                    command += ", "
                command += str(segmentTuple)
        command += ";"
        return command
        
    def updateImageRepositoryStatus(self, freeDiskSpace, availableDiskSpace, status) :
        """
        Updates the image repository's status
        Args:
            freeDiskSpace: the free disk space in the image repository
            availableDiskSpace: the available disk space in the image repository
            status: the image repository's connection status
        Returns:
            Nothing
        """
        query = "SELECT * FROM ImageRepositoryStatus;"
        result = self._executeQuery(query, True)
        if (result == None) :
            command = "INSERT INTO ImageRepositoryStatus VALUES (1, {0}, {1}, '{2}');".format(freeDiskSpace, availableDiskSpace, status)
        else :
            command = "UPDATE ImageRepositoryStatus SET freeDiskSpace = {0}, availableDiskSpace = {1}, repositoryStatus = '{2}';"\
                .format(freeDiskSpace, availableDiskSpace, status)
        self._executeUpdate(command)
    
    def addNewImage(self, temporaryID, baseImageID, ownerID, imageName, imageDescription):
        """
        Registers a new image in the database
        Args:
            temporaryID: an temporary image ID
            baseImageID: an existing image ID
            ownerID: the image owner's ID
            imageName: the new image's name
            imageDescription: the new image's description
        Returns:
            Nothing
        """
        baseImageData = self.getImageData(baseImageID)
        update = "INSERT INTO EditedImage VALUES('{0}', {1}, {2}, '{3}', '{4}', {5}, {6}, {7}, {8}, 0);"\
            .format(temporaryID, baseImageData["VanillaImageFamilyID"], -1, imageName, imageDescription,
                    baseImageData["OSFamily"], baseImageData["OSVariant"], ownerID, EDITION_STATE_T.TRANSFER_TO_VM_SERVER)
        self._executeUpdate(update)
        
    def editImage(self, commandID, imageID, ownerID):
        """
        Registers an edit images in the database
        Args:
            commandID: the image edition command's ID
            imageID: the edited image's ID
            ownerID: the image owner's ID
        Returns:
            Nothing
        """
        query = "SELECT * from EditedImage WHERE imageID = {0};".format(imageID)
        if (self._executeQuery(query, True) != None) :
            update = "UPDATE EditedImage SET temporaryID = '{0}', state = {2} WHERE imageID = {1};".format(commandID, imageID, EDITION_STATE_T.TRANSFER_TO_VM_SERVER)
            self._executeUpdate(update)
        else :
            imageData = self.getImageData(imageID)
            update = "DELETE FROM Image WHERE imageID = {0};".format(imageID)
            self._executeUpdate(update)
            update = "INSERT INTO EditedImage VALUES('{0}', {1}, {2}, '{3}', '{4}', {5}, {6}, {7}, {8}, 1);"\
                .format(commandID, imageData["VanillaImageFamilyID"], imageID, imageData["ImageName"], imageData["ImageDescription"],
                        imageData["OSFamily"], imageData["OSVariant"], ownerID, EDITION_STATE_T.TRANSFER_TO_VM_SERVER)
            self._executeUpdate(update)
            
    def moveRowToImage(self, temporaryID):
        """
        Moves a row from the EditedImage table to the Image table
        Args:
            temporaryID: a temporary image ID
        Returns:
            Nothing
        """
        imageData = self.getImageData(temporaryID)
        update = "INSERT INTO Image VALUES ({0}, {1}, '{2}', '{3}', {4}, {5}, {6}, 1);"\
            .format(imageData["ImageID"], imageData["VanillaImageFamilyID"], imageData["ImageName"], imageData["ImageDescription"],
                    imageData["OSFamily"], imageData["OSVariant"], int(imageData["IsBaseImage"]))
        self._executeUpdate(update)
        update = "DELETE FROM EditedImage WHERE temporaryID = '{0}';".format(temporaryID)
        self._executeUpdate(update)
        
    def deleteEditedImage(self, temporaryID):
        """
        Deletes a new or an edited image from the database
        Args:
            temporaryID: a temporary image ID
        Returns:
            Nothing
        """
        update = "DELETE FROM EditedImage WHERE temporaryID = '{0}';".format(temporaryID)
        self._executeUpdate(update)
        
    def deleteImage(self, imageID):
        """
        Deletes an existing image from the database
        Args:
            imageID: the affected image's ID
        Returns:
            Nothing
        """
        update = "DELETE FROM Image WHERE imageID = {0}".format(imageID)
        self._executeUpdate(update)
        
    def updateEditedImageState(self, temporaryID, newState, expectedState=None):
        """
        Updates an edited image status in the database
        Args:
            temporaryID: the image's temporary ID
            newState: the image's new state
            expectedState: the image's expected state. If it's not none, the edited image state will only
            be updated when its current state and expectedState are equals.
        """
        if (expectedState != None) : 
            query = "SELECT state FROM EditedImage WHERE temporaryID = '{0}';".format(temporaryID)
            if (self._executeQuery(query, True) != expectedState) :
                return
        update = "UPDATE EditedImage SET state = {1} WHERE temporaryID = '{0}';".format(temporaryID, newState)
        self._executeUpdate(update)
        
    def registerImageID(self, temporaryID, imageID):
        """
        Registers an image ID in the database
        Args:
            temporaryID: the image's temporary ID
            imageID: the image's ID
        Returns:
            Nothing
        """
        update = "UPDATE EditedImage SET imageID = {1}, state = {2} WHERE temporaryID = '{0}';".format(temporaryID, imageID, EDITION_STATE_T.CHANGES_NOT_APPLIED)
        self._executeUpdate(update)
        
    def makeBootable(self, imageID):
        """
        Marks an image as bootable
        Args:
            imageID: the affected image's ID
        Returns:
            Nothing
        """
        update = "UPDATE Image SET isBootable = 1 WHERE imageID = {0};".format(imageID)
        self._executeUpdate(update)
        
    def __getDomainUID(self, serverName, ownerID, imageID):
        query = "SELECT domainUID FROM ActiveVirtualMachines WHERE serverName = '{0}' AND ownerID = {1} AND imageID = {2};"\
            .format(serverName, ownerID, imageID)
        return self._executeQuery(query, True)
        
    def unregisterDomain(self, domainUID):
        """
        Unregisters a domain in the databse
        Args:
            domainUID: the domain's ID
        Returns:
            Nothing
        """
        update = "DELETE FROM ActiveVirtualMachines WHERE domainUID = '{0}';".format(domainUID)
        self._executeUpdate(update)
        
    def affectsToNewOrEditedImage(self, autoDeploymentCommandID):
        """
        Checks if an auto-deployment command affects to an image edition or an image creation command
        Args:
            autoDeploymentCommandID: the auto-deployment command's ID
        Returns:
            Nothing
        """
        query = "SELECT * FROM EditedImage WHERE temporaryID = '{0}';".format(autoDeploymentCommandID)
        return self._executeQuery(query, True) != None