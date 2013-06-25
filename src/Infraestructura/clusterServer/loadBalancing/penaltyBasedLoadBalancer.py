# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: penaltyBasedLoadBalancer.py    
    Version: 4.0
    Description: penalty-based load balancer implementation
    
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

from loadBalancer import LoadBalancer, MODE_T
from errors.codes import ERROR_DESC_T

class PenaltyBasedLoadBalancer(LoadBalancer):
    '''
    This class implements the penalty-based load balancing algorithm. It tries
    to distribute the workload equally among the active virtual machine servers.
    '''
    
    def __init__(self, databaseConnector, vCPUsWeight, vCPUsExcessThreshold, ramWeight, storageSpaceWeight, temporarySpaceWeight):
        """
        Initializes the load balancer's state
        Args:
            databaseConnector: a cluster server database connector
            vCPUsWeight: the virtual CPUs weight
            vCPUsExcessThreshold: the virtual CPUs excess threshold. If it's greater than one, the hosted virtual machines
                may use a number of virtual CPUs that is higher than the number of physical CPUs of the virtual machine server.
            ramWeight: the RAM weight
            storageSpaceWeight: the storage space weight
            temporarySpaceWeight: the temporary space weight
        """
        LoadBalancer.__init__(self, databaseConnector)
        self.__vCPUsWeight = vCPUsWeight
        self.__vCPUsExcessThreshold = vCPUsExcessThreshold
        self.__ramWeight = ramWeight
        self.__storageSpaceWeight = storageSpaceWeight
        self.__temporarySpaceWeight = temporarySpaceWeight
        
    def assignVMServer(self, imageID, mode):
        '''
        Determines what virtual machine server will host an image.
        Args:
            imageID: the image's ID
            mode: the operation that the virtual machine server will perform (i.e. boot a virtual
                machine that uses the specified image, deploy an image,...)
        Returns:
            a tuple (server IDs, errorMessage, copies), where server IDs is a list containing the
            chosen servers IDs, errorMessage is an error message and copies is the number of
            copies that can be hosted on the chosen servers.
        '''
        
        # Step 1: determine which virtual machine servers can be used
        
        if (mode == MODE_T.BOOT_DOMAIN) :
            availableServers = self._dbConnector.getHosts(imageID)
            errorDescription = ERROR_DESC_T.CLSRVR_IMAGE_NOT_AVAILABLE
        elif (mode == MODE_T.CREATE_OR_EDIT_IMAGE):
            availableServers = self._dbConnector.getVanillaVMServers()
            errorDescription = ERROR_DESC_T.CLSRVR_NO_EDITION_SRVRS
        else:
            availableServers = self._dbConnector.getCandidateVMServers(imageID)
            errorDescription = ERROR_DESC_T.CLSRVR_NO_CANDIDATE_SRVRS
            
        if (len(availableServers) == 0) :
            return (0, errorDescription)
            
        # Step 2: obtain the image's virtual machine family features
        
        vmFamilyID = self._dbConnector.getImageVMFamilyID(imageID)
        if (vmFamilyID == None) :
            return (0, ERROR_DESC_T.CLSRVR_UNKNOWN_IMAGE)            
        
        imageFeatures = self._dbConnector.getVMFamilyFeatures(vmFamilyID)       
        
        # Step 3: compute the penalties. If it's necessary, the number of instance
        # that can be hosted will also be calculated.
        
        serverPenalties = []
        
        for serverID in availableServers :            
            serverStatusData = self._dbConnector.getVMServerStatistics(serverID)
            normalizedVCPUPenalty = float(imageFeatures["vCPUs"] + serverStatusData["ActiveVCPUs"]) / serverStatusData["PhysicalCPUs"]
            normalizedRAMPenalty = float(imageFeatures["RAMSize"] + serverStatusData["RAMInUse"]) / serverStatusData["RAMSize"]
            normalizedStorageSpacePenalty = float(imageFeatures["osDiskSize"] + serverStatusData["AvailableStorageSpace"]
                                                      - serverStatusData["FreeStorageSpace"]) / serverStatusData["AvailableStorageSpace"]
            normalizedTemporarySpacePenalty = float(imageFeatures["dataDiskSize"] + serverStatusData["AvailableTemporarySpace"]
                                                      - serverStatusData["FreeTemporarySpace"]) / serverStatusData["AvailableTemporarySpace"]            
                    
            if (normalizedVCPUPenalty <= (1 + self.__vCPUsExcessThreshold) or normalizedRAMPenalty <= 1 
                    or normalizedStorageSpacePenalty <= 1 or normalizedTemporarySpacePenalty <= 1) :
                # An instance fits on this virtual machine server => we don't discard it
                serverPenalty = self.__vCPUsWeight * normalizedVCPUPenalty + self.__ramWeight * normalizedRAMPenalty + \
                    self.__storageSpaceWeight * normalizedStorageSpacePenalty + self.__temporarySpaceWeight * normalizedTemporarySpacePenalty     
                if (mode != MODE_T.DEPLOY_IMAGE) :                
                    serverPenalties.append((serverID, serverPenalty))    
                else :
                    copies_with_cpus = serverStatusData["PhysicalCPUs"] / imageFeatures["vCPUs"]
                    copies_with_RAM = serverStatusData["RAMSize"] / imageFeatures["RAMSize"]
                    copies_with_temporaryDiskSpace = serverStatusData["AvailableTemporarySpace"] / imageFeatures["dataDiskSize"]
                    values = [copies_with_cpus, copies_with_RAM, copies_with_temporaryDiskSpace]
                    serverPenalties.append((serverID, serverPenalty, min(values)))    
                
        if (serverPenalties == []) :
            if (mode == MODE_T.CREATE_OR_EDIT_IMAGE) :
                errorDescription = ERROR_DESC_T.CLSRVR_EDITION_VMSRVRS_UNDER_FULL_LOAD
            else :
                errorDescription = ERROR_DESC_T.CLSRVR_VMSRVRS_UNDER_FULL_LOAD
            return (0, errorDescription)
        
        # Step 4: Sort the servers by their penalties
        
        serverPenalties.sort(key=lambda tupl : tupl[1])    
        
        # Return the results         
        
        if (mode != MODE_T.DEPLOY_IMAGE) :
            # We choose the virtual machine server with less penalty
            return (serverPenalties[0][0], None)
        else :
            copies = 0
            servers = []
            for tup in serverPenalties :
                servers.append((tup[0], tup[2]))
                copies += tup[2]
            return (servers, None, copies)