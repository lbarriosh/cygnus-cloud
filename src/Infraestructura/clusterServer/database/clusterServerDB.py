# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: clusterServerDB.py    
    Version: 5.0
    Description: cluster server database connector
    
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


from ccutils.databases.connector import BasicDBConnector
import time
from clusterServer.database.image_state_t import IMAGE_STATE_T
from clusterServer.database.server_state_t import SERVER_STATE_T

class ClusterServerDatabaseConnector(BasicDBConnector):
    """
    Cluster server database connector
    """
    def __init__(self, sqlUser, sqlPassword, databaseName):
        '''
            Initializes the connector's state
            Args:
                sqlUser: a MySQL user
                sqlPassword: the MySQL user's password
                databaseName: a database name
            Returns:
                Nothing
        '''
        BasicDBConnector.__init__(self, sqlUser, sqlPassword, databaseName)
        
    def deleteVMServerStatistics(self, serverID):
        '''
            Deletes the statistics data associated with a virtual machine server
            Args:
                serverId: the virtual machine server's ID
            Returns:
                Nothing
        '''
        command = "DELETE FROM VMServerStatus WHERE serverId = {0}".format(serverID)
        self._executeUpdate(command)
        command = "DELETE FROM AllocatedVMServerResources WHERE serverID = {0};".format(serverID)
        self._executeUpdate(command)
        
    def getVMServerConfiguration(self, serverId):
        '''
            Returns a virtual machine server's current configuration
            Args:
                serverId: the virtual machine server's ID
            Returns:
                A dictionary containing the virtual machine server's current configuration
        '''
        query = "SELECT serverName, serverStatus, serverIP, serverPort, isEditionServer FROM VMServer"\
            + " WHERE serverId = '{0}';".format(serverId)
        result = self._executeQuery(query, True)
        if (result == None) : 
            return None
        d = dict()
        (name, status, ip, port, isEditionServer) = result
        d["ServerName"] = name
        d["ServerStatus"] = status
        d["ServerIP"] = ip
        d["ServerPort"] = port
        d["IsEditionServer"] = isEditionServer == 1
        return d         
    
    def getVMServerStatisticsToSend(self, serverID):
        """
        Returns a virtual machine server's current resource usage. This information will be
        sent to the cluster endpoint daemon.
        Args:
            serverID: the virtual machine server's ID
        Returns:
                A dictionary containing the virtual machine server's current resource usage
        """
        result = self.getVMServerStatistics(serverID)
        if (result == None) :
            return None
        result["ServerName"] = str(self.getVMServerConfiguration(serverID)["ServerName"])        
        return result     
        
    def getVMServerStatistics(self, serverID) :
        '''
            Returns a virtual machine server's current resource usage
            Args:
                serverId: the virtual machine server's ID
            Returns:
                A dictionary containing the virtual machine server's current resource usage
        '''
        query = "SELECT hosts, ramInUse, ramSize, freeStorageSpace, availableStorageSpace,\
            freeTemporarySpace, availableTemporarySpace, activeVCPUs, physicalCPUs FROM VMServerStatus WHERE serverId = {0};".format(serverID)
        result = self._executeQuery(query, True)
        if (result == None) : 
            return None            
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
        
        query = "SELECT SUM(ramInUse), SUM(freeStorageSpace), SUM(freeTemporarySpace), SUM(activeVCPUs), SUM(activeHosts) FROM AllocatedVMServerResources \
            WHERE serverId = {0};".format(serverID)
        result = self._executeQuery(query, True)
        if (result[0] != None) :
            d["RAMInUse"] += int(round(result[0]))
            d["FreeStorageSpace"] -= int(round(result[1]))
            d["FreeTemporarySpace"] -= int(round(result[2]))
            d["ActiveVCPUs"] += int(round(result[3]))
            d["ActiveHosts"] += int(round(result[3]))
        
        return d
    
    def getVMServerIDs(self):
        '''
            Returns all the registered virtual machine servers' IDs.
            Args: 
                None
            Returns:
                A list containing  all the registered virtual machine servers' IDs.
        '''
        query = "SELECT serverId FROM VMServer;"  
        results=self._executeQuery(query)
        if (results == None) :
            return []
        serverIds = []
        for r in results:
            serverIds.append(r)
        return serverIds
    
    def getActiveVMServersConnectionData(self):
        """
        Returns the active servers' IP addresses.
        Args:
            None
        Returns: 
            A list containing the active servers' IP addresses.
        """
        query = "SELECT serverIP, serverPort FROM VMServer WHERE serverStatus = " + str(SERVER_STATE_T.READY) + ";"
        results = self._executeQuery(query)
        if (results == None) :
            return []
        serverIPs = []
        for r in results :
            serverIPs.append({"ServerIP" : r[0], "ServerPort" : r[1]})
        return serverIPs
        
        
    def registerVMServer(self, name, IPAddress, port, isEditionServer):
        '''
            Registers a new virtual machine server on the database.
            Args:
                name: the new virtual machine server's name
                IPAddress: the new virtual machine server's IP address
                port: the new virtual machine server's port
                isEditionServer: indicates whether the new virtual machine server will be used
                    to create or edit images or not.
            Returns:
                The new virtual machine server's ID
        '''
        if (isEditionServer) :
            vanillaValue = 1
        else :
            vanillaValue = 0
        
        update = "INSERT INTO VMServer(serverStatus, serverName, serverIP, serverPort, isEditionServer) VALUES ({0}, '{1}', '{2}', {3}, {4});"\
            .format(SERVER_STATE_T.BOOTING, name, IPAddress, port, vanillaValue)
        self._executeUpdate(update)      
        query = "SELECT serverId FROM VMServer WHERE serverIP ='" + IPAddress + "';"
        serverId = self._executeQuery(query)[-1]
        return serverId
    
    def deleteVMServer(self, serverNameOrIPAddress):
        '''
            Unregisters a virtual machine server from the database
            Args:
                serverNameOrIPAddress: a virtual machine server's name or IP address 
            Returns:
                Nothing
        '''
        serverId = self.getVMServerID(serverNameOrIPAddress)
        query = "DELETE FROM VMServer WHERE serverId = " + str(serverId) + ";"
        self._executeUpdate(query)
        self.deleteVMServerStatistics(serverId)
        
    def getImageIDs(self):
        """
            Returns the registered images' IDs
            Args:
                None
            Returns:
                A list containing the registered images' IDs.
        """
        query = "SELECT DISTINCT imageId FROM ImageOnServer;"
        results = self._executeQuery(query)
        imageIDs = []
        for r in results:
            imageIDs.append(r)
        return imageIDs
        
    def getHosts(self, imageId, imageStatus = IMAGE_STATE_T.READY):
        '''
            Checks which virtual machine servers contain a image in the specified
            state and returns their identifiers.
            Args:
                imageId: the image's ID
            Returns:
                a list containing the hosts' IDs.
        '''
        query = "SELECT ImageOnServer.serverId FROM ImageOnServer\
            INNER JOIN VMServer ON ImageOnServer.serverId = VMServer.serverID \
                WHERE VMServer.serverStatus = {0} AND imageId = {1} AND status = {2};".format(SERVER_STATE_T.READY, imageId, imageStatus) 
        results=self._executeQuery(query)
        if (results == None) :
            return []
        return results
    
    def getCandidateVMServers(self, imageID) :
        """
        Checks which active virtual machine servers do not contain a disk image.
        Args:
            imageID: the image's ID
        Returns:
            a list containing the candidate servers' IDs.
        """
        query = "SELECT VMServer.serverId FROM VMServer WHERE serverStatus = {0} AND NOT EXISTS (SELECT * FROM ImageOnServer\
            WHERE ImageOnServer.serverId = VMServer.serverID AND ImageOnServer.imageId = {1});".format(SERVER_STATE_T.READY, imageID)
        results=self._executeQuery(query)
        if (results == None) :
            return []
        return results
    
    def initializeVMServersStatus(self):
        """
        Initializes all the registered virtual machine servers' status.
        Args:
            None
        Returns:
            Nothing
        """
        vmServerIDs = self.getVMServerIDs()
        for vmServerID in vmServerIDs :
            self.updateVMServerStatus(vmServerID, SERVER_STATE_T.SHUT_DOWN)
    
    def getHostedImages(self, serverID):
        '''
            Checks which images are hosted on a virtual machine server.
            Args:
                serverID: the virtual machine server's ID.
            Returns:
                a list containing the hosted images' IDs.
        '''
        query = "SELECT VMServer.serverName, imageId, status FROM VMServer, ImageOnServer " +\
                 "WHERE VMServer.serverId = ImageOnServer.serverId AND VMServer.serverID = {0};"\
                 .format(serverID)
        results=self._executeQuery(query)
        if (results == None) :
            return []
        retrievedData = []
        for r in results:
            retrievedData.append({"ServerName" : str(r[0]), "ImageID" : int(r[1]), "CopyStatus": int(r[2])})
        return retrievedData
    
    def hostsImage(self, serverID, imageID):
        """
        Checks if a virtual machine server hosts an image.
        Args:
            serverID: the virtual machine server's ID
            imageID: the image's ID
        Returns:
            True if the virtual machine server hosts the given image, and False if it doesn't.
        """
        query = "SELECT * FROM ImageOnServer WHERE serverId = {0} AND imageID = {1};".format(serverID, imageID)
        result = self._executeQuery(query, True)
        return result != None
    
    def getVMServerID(self, nameOrIPAddress):
        '''
        Returns a virtual machine server's ID from its name or IP address.
        Args:    
            nameOrIPAddress: the virtual machine server's name or IP address
        Returns:
            The virtual machine server's ID
        '''
        query = "SELECT serverId FROM VMServer WHERE serverIP = '" + nameOrIPAddress +\
             "' OR serverName = '" + nameOrIPAddress + "';"
        results=self._executeQuery(query, True)
        if (results == None) : 
            return None
        return results
    
    def updateVMServerStatus(self, serverId, newStatus):
        '''
            Updates a virtual machine server's status
            Args:
                serverId: the virtual machine server's ID
                newStatus: the virtual machine server's new status
            Returns:
                Nothing
        '''
        command = "UPDATE VMServer SET serverStatus=" + str(newStatus) + \
            " WHERE serverId = " + str(serverId) + ";"
        # Execute it
        self._executeUpdate(command)
        
        
    def getServerImages(self, serverId):
        '''
            Returns una lista con los identificadores de las imágenes asociadas a un servidor 
              de máquinas virtuales.
            Args:
                serverId: el identificador del servidor de máquinas virtuales
            Returns:
                Lista con los identificadores de las imágenes
            Nota: este método está modificado para que un solo objeto me sirva para 
            leer la base de datos. Tal y como estaba, tenía que tener un objeto ImageServerManager
            para cada servidor de máquinas virtuales, y eso son muchas conexiones.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT imageId, status FROM ImageOnServer WHERE serverId = {0}; ".format(serverId)    
        #Recogemos los resultado
        results=self._executeQuery(sql)
        #Guardamos en una lista los ids resultantes
        serverIds = []
        for r in results:
            serverIds.append((r[0], r[1]))
        #Devolvemos la lista resultado
        return serverIds
         
    def assignImageToServer(self, serverID, imageID, status = IMAGE_STATE_T.READY):
        '''
        Asigna una imagen a un servidor de máquinas virtuales
        Args:
            serverID: identificador único del servidor de máquinas virtuales
            imageID: identificador único de la imagen
        Returns:
            Nothing.
        '''
        # Insert the row in the table
        query = "INSERT INTO ImageOnServer VALUES({0}, {1}, {2});".format(serverID, imageID, status)
        self._executeUpdate(query)
        
    def deleteImageFromServer(self, serverID, imageID):
        update = "DELETE FROM ImageOnServer WHERE serverId = {0} AND imageId = {1}".format(serverID, imageID)
        self._executeUpdate(update)
        
    def setVMServerStatistics(self, serverID, runningHosts, ramInUse, ramSize, freeStorageSpace,
                              availableStorageSpace, freeTemporarySpace, availableTemporarySpace,
                              activeVCPUs, physicalCPUs):
        '''
        Actualiza las estadísticas de un servidor de máquinas virtuales.
        Args
        '''
        query = "INSERT INTO VMServerStatus VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9});".format(serverID, runningHosts, 
            ramInUse, ramSize, freeStorageSpace, availableStorageSpace, freeTemporarySpace, availableTemporarySpace,
                              activeVCPUs, physicalCPUs)
        try :
            self._executeUpdate(query)
        except Exception :
            query = "UPDATE VMServerStatus SET hosts = {0}, ramInUse = {1}, ramSize = {2}, freeStorageSpace = {3},\
                availableStorageSpace = {4}, freeTemporarySpace = {5}, availableTemporarySpace = {6},\
                activeVCPUs = {7}, physicalCPUs = {8}  WHERE serverId = {9};".format(runningHosts, ramInUse, ramSize, freeStorageSpace,
                              availableStorageSpace, freeTemporarySpace, availableTemporarySpace,
                              activeVCPUs, physicalCPUs, serverID)
            self._executeUpdate(query)
        
        update = "DELETE FROM AllocatedVMServerResources WHERE serverID = {0} AND freeStorageSpace = 0 AND remove = 1;".format(serverID)
        self._executeUpdate(update)
        
        update = "UPDATE AllocatedVMServerResources SET freeStorageSpace = 0, remove = 0 WHERE remove = 1 AND freeStorageSpace <> 0;"
        self._executeUpdate(update)
            
            
        
    def setServerBasicData(self, serverId, name, status, IPAddress, port, isEditionServer):
        '''
            Modifica los datos básicos de un servidor de máquinas virtuales
            Args:
                name: nuevo nombre del servidor
                status: nuevo estado del servidor
                IPAddress: nueva IP del servidor
                port: nuevo puerto del servidor
                isEditionServer: indica si el servidor se usará preferentemente para editar imágenes o no
            Returns:
                Nothing
        '''
        if (isEditionServer) : vanillaValue = 1
        else : vanillaValue = 0
        
        query = "UPDATE VMServer SET serverName = '{0}', serverIP = '{1}', serverPort = {2}, serverStatus = {3}, isEditionServer = {4}\
            WHERE serverID = {5};".format(name, IPAddress, port, status, vanillaValue, serverId);
        
        self._executeUpdate(query)
        
    def registerVMBootCommand(self, commandID, vmID):
        """
        Registers a virtual machine boot command in the database.
        Args:
            commandID: the virtual machine boot command's unique identifier
        Returns:
            Nothing
        """
        timestamp = time.time()
        update = "INSERT INTO VMBootCommand VALUES ('{0}', {1}, {2});".format(commandID, timestamp, vmID)
        self._executeUpdate(update)
        
    def removeVMBootCommand(self, commandID):
        """
        Removes a virtual machine boot command from the database
        Args:
            commandID: the command's unique identifier
        Returns:
            Nothing
        """
        update = "DELETE FROM VMBootCommand WHERE commandID = '{0}';".format(commandID)        
        self._executeUpdate(update)
        
    def getOldVMBootCommandID(self, timeout):
        """
        Removes an old virtual machine command id from the database and returns it.
        Args:
            the timeout. A command will be considered old when its timestamp plus timeout
            is greater than or equal to the current time.
        Returns:
            If an old commandID is found, it will be returned. Otherwise, None will be returned
        """
        query = "SELECT * FROM VMBootCommand;"
        results = self._executeQuery(query, False)
        if (results == None) :
            return None
        currentTime = time.time()
        for row in results :
            difference = currentTime - row[1]
            if (difference >= timeout) :
                update = "DELETE FROM VMBootCommand WHERE commandID = '{0}'".format(row[0])
                self._executeUpdate(update)
                return (row[0], int(row[2])) # Match! -> return it
        return None
    
    def getVMBootCommandData(self, commandID):
        query = "SELECT * FROM VMBootCommand WHERE commandID = '{0}';".format(commandID)
        result = self._executeQuery(query, True)
        if (result == None) : return None
        else :
            return (result[0], int(result[2]))
    
    def registerActiveVMLocation(self, vmID, serverID):
        """
        Registra la ubicación de una nueva máquina virtual activa
        Args:
            vmID: el identificador único de la máquina virtual
            serverID: el identificador único del servidor de máquinas virtuales
            que la alberga.
        Returns:
            Nothing
        """
        update = "INSERT INTO ActiveVMDistribution VALUES ('{0}',{1});".format(vmID, serverID)
        self._executeUpdate(update)
        
    def deleteActiveVMLocation(self, vmID):
        """
        Elimina la ubicación de una máquina virtual activa
        Args:
            vmID: el identificador único de la máquina virtual
        Returns:
            Nothing
        """
        update = "DELETE FROM ActiveVMDistribution WHERE vmID = '{0}';".format(vmID);
        self._executeUpdate(update)
        
    def getActiveVMHostID(self, vmID):
        """
        Returns la ubicación de una máquina virtual activa
        Args:
            vmID: el identificador único de la máquina virtual
        Returns:
            El identificador único del servidor de máquinas virtuales 
            que alberga la máquina virtual
        """
        query = "SELECT serverID FROM ActiveVMDistribution WHERE vmID = '{0}';".format(vmID)
        result = self._executeQuery(query, True)
        if result == None :
            return None
        else :
            return result
        
    def getVanillaVMServers(self):
        query = "SELECT serverID FROM VMServer WHERE isEditionServer = 1 AND serverStatus = {0};".format(SERVER_STATE_T.READY)
        result = self._executeQuery(query, False)
        if (result == None) :
            return []
        else :
            return result
    
    def deleteHostedVMs(self, serverID):
        """
        Borra la ubicación de todas las máquinas virtuales activas registradas en un servidor
        de máquinas virtuales.
        Args:
            serverID: el identificador único del servidor de máquinas virtuales
        Returns:
            Nothing
        """
        update = "DELETE FROM ActiveVMDistribution WHERE serverID = {0};".format(serverID)
        self._executeUpdate(update)
        
    def registerHostedVMs(self, serverID, hostedVMs):
        """
        Registers the virtual machines that are hosted on a virtual machine server.
        Args:
            serverID: the host's ID
            hostedVMs: a list containing the hosted virtual machines' IDs
        Returns:
            Nothing
        """
        update = "DELETE FROM ActiveVMDistribution WHERE serverID = {0};".format(serverID)
        self._executeUpdate(update)
        update = "INSERT INTO ActiveVMDistribution VALUES ('{0}',{1});"
        for hostedDomainUID in hostedVMs :
            self._executeUpdate(update.format(hostedDomainUID, serverID))
            
    def getVMFamilyFeatures(self, familyID):
        """
        Returns a virtual machine familyID's features
        Args:
            familyID: teh virtual machine server's ID
        Returns:
            A dictionary containing the virtual machine family's features
        """
        query = "SELECT ramSize, vCPUs, osDiskSize, dataDiskSize FROM VMFamily WHERE familyID = {0}".format(familyID)
        results=self._executeQuery(query)
        if (results == ()) : 
            return None
        (ram, vCPUs, OSDiskSize, dataDiskSize) = results[0]
        d = dict() 
        d["RAMSize"] = ram
        d["vCPUs"] = vCPUs
        d["osDiskSize"] = OSDiskSize
        d["dataDiskSize"] = dataDiskSize
        return d
        
    def getVMFamilyID(self, familyName):
        """
        Returns a virtual machine family's ID
        Args:
            familyName: the virtual machine family's name
        Returns:
            the virtual machine server family's ID
        """
        query = "SELECT familyID FROM VMFamily WHERE familyName = '{0}';".format(familyName)
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            return int(result)
    
    def getVMResources(self, imageID):
        """
        Returns the resources associated to an image's virtual machine family.
        Args:
            imageID: an image ID
        Returns:
            A dictionary containing the resources associated to the image's virtual machine family.
        """
        query = "SELECT * FROM VMFamilyOf WHERE familyID = {0}".format(imageID)
        results=self._executeQuery(query)
        if (results == ()) : 
            return None
        (vanillaID, imageID) = results
        return self.getVMFamilyFeatures(vanillaID)
    
    def getImageVMFamilyID(self, imageID):
        """
        Returns an image virtual machine family's ID
        Args:
            imageID: an imge ID
        Returns:
            the image virtual machine server family's ID
        """
        query = "SELECT familyID FROM VMFamilyOf WHERE imageID = {0};".format(imageID)
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            return int(result)
        
    def registerImageVMFamilyID(self, imageID, familyID):
        """
        Registers an image's virtual machine family
        Args:
            imageID: an image ID
            familyID: a virtual machine family ID
        Returns:
            Nothing
        """
        update = "INSERT INTO VMFamilyOf VALUES ({0}, {1});".format(imageID, familyID)
        self._executeUpdate(update)
        
    def deleteImageVMFamilyID(self, imageID):
        """
        Unregisters an image's virtual machine family
        Args:
            imageID: an image ID
        Returns:
            Nothing
        """
        update = "DELETE FROM VMFamilyOf WHERE imageID = {0}".format(imageID)
        self._executeUpdate(update)
        
    def addImageRepository(self, repositoryIP, repositoryPort, status):
        """
        Registers an image repository
        Args:
            repositoryIP: the image repository's IP address
            repositoryPort: the image repository's port
            status: the image repository's status
        Returns:
            Nothing
        """
        command = "INSERT INTO ImageRepository VALUES ('{0}', {1}, 0, 0, {2})".format(repositoryIP, repositoryPort, status)
        self._executeUpdate(command)
        
    def updateImageRepositoryStatus(self, repositoryIP, repositoryPort, freeDiskSpace, availableDiskSpace):
        """
        Updates an image repository's status
        Args:
            repositoryIP: the image repository's IP address
            repositoryPort: the image repository's port
            freeDiskSpace: the image repository's free disk space
            availableDiskSpace: the image repository's available disk space
        Returns:
            Nothing
        """
        command = "UPDATE ImageRepository SET freeDiskSpace={2}, availableDiskSpace={3} WHERE repositoryIP = '{0}' AND repositoryPort = {1};"\
            .format(repositoryIP, repositoryPort, freeDiskSpace, availableDiskSpace)
        self._executeUpdate(command)
        command = "DELETE FROM AllocatedImageRepositoryResources WHERE repositoryIP = '{0}' AND repositoryPort = {1} AND remove = 1".format(repositoryIP, repositoryPort)
        self._executeUpdate(command)
        
    def updateImageRepositoryConnectionStatus(self, repositoryIP, repositoryPort, status):
        """
        Updates an image repository's connection status
        Args:
            repositoryIP: the image repository's IP address
            repositoryPort: the image repository's port
            status: the current image repository's connection status
        Returns:
            Nothing
        """
        command = "UPDATE ImageRepository SET connection_status={2} WHERE repositoryIP = '{0}' AND repositoryPort = {1};"\
            .format(repositoryIP, repositoryPort, status)
        self._executeUpdate(command)
        
    def getImageRepositoryStatus(self, repositoryIP, repositoryPort):
        """
        Returns an image repository's curremt status data
        Args:
            repositoryIP: the image repository's IP address
            repositoryPort: the image repository's port
        Returns:
            A dictionary containing the image repository's current status data
        """
        query = "SELECT freeDiskSpace, availableDiskSpace, connection_status FROM ImageRepository WHERE repositoryIP = '{0}' AND repositoryPort = {1};"\
            .format(repositoryIP, repositoryPort)
        result = self._executeQuery(query, True)
        if (result == None or result[2] != SERVER_STATE_T.READY):
            return None
        query = "SELECT SUM(allocatedDiskSpace) FROM AllocatedImageRepositoryResources WHERE repositoryIP = '{0}' AND repositoryPort={1};".\
            format(repositoryIP, repositoryPort)
        allocatedSpace = self._executeQuery(query, True)
        status =  {"FreeDiskSpace" : result[0], "AvailableDiskSpace" : result[1], "ConnectionStatus" : result[2]}
        if (allocatedSpace != None) :
            status["FreeDiskSpace"] += int(round(allocatedSpace))
        return status
        
    def allocateImageRepositoryResources(self, repositoryIP, repositoryPort, commandID, diskSpace):
        """
        Allocates disk space on an image repository
        Args:
            repositoryIP: the image repository's IP address
            repositoryPort: the image repository's port
            commandID: a command ID
            diskSpace: the allocated disk space
        Returns:
            Nothing
        """
        update = "INSERT INTO AllocatedImageRepositoryResources VALUES ('{0}', '{1}', {2}, {3}, 0)".format(commandID, repositoryIP, repositoryPort, diskSpace)
        self._executeUpdate(update)
        
    def freeImageRepositoryResources(self, commandID, error):
        """
        Frees a part of the allocated disk space on an image repository
        Args:
            commandID: a command ID
            error: indicates if an error was detected while processing the command or not.
        Returns:
            Nothing
        """
        if (error) :
            update = "DELETE FROM AllocatedImageRepositoryResources WHERE commandID = '{0}';".format(commandID)
        else :
            update = "UPDATE AllocatedImageRepositoryResources SET remove = 1 WHERE commandID = '{0}';".format(commandID)
        self._executeUpdate(update)
        
    def registerNewImageVMFamily(self, temporaryID, familyID):
        """
        Registers a new image's virtual machine family
        Args:
            temporaryID: the new image's temporary ID
            familyID: the new image's virtual machine family ID
        Returns:
            Nothing
        """
        update = "INSERT INTO VMFamilyOfNewVM VALUES ('{0}', {1});".format(temporaryID, familyID)
        self._executeUpdate(update)
        
    def getNewImageVMFamily(self, temporaryID):
        """
        Returns a new image's virtual machine family ID
        Args:
            temporaryID: a new image's temporary ID
        Returns:
            the new image's virtual machine family ID
        """
        query = "SELECT familyID FROM VMFamilyOfNewVM WHERE temporaryID = '{0}';".format(temporaryID)
        return self._executeQuery(query, True)
        
    def deleteNewImageVMFamily(self, temporaryID):
        """
        Deletes a new image's virtual machine family ID
        Args:
            temporaryID: the new image's temporary ID
        Returns:
            Nothing
        """
        update = "DELETE FROM VMFamilyOfNewVM WHERE temporaryID = '{0}';".format(temporaryID)
        self._executeUpdate(update)
        
    def addImageEditionCommand(self, commandID, imageID):
        """
        Registers an image edition command
        Args:
            commandID: the command's ID
            imageID: the affected image's ID
        Returns:
            Nothing
        """
        self.__addImageCommand("ImageEditionCommand", commandID, imageID)
        
    def addImageDeletionCommand(self, commandID, imageID):
        """
        Registers an image deletion command
        Args:
            commandID: the command's ID
            imageID: the affected image's ID
        Returns:
            Nothing
        """
        self.__addImageCommand("ImageDeletionCommand", commandID, imageID)
        
    def __addImageCommand(self, tableName, commandID, imageID):
        update = "INSERT INTO {0} VALUES('{1}', {2});".format(tableName, commandID, imageID)
        self._executeUpdate(update)
        
    def removeImageEditionCommand(self, commandID):
        """
        Unregisters an image edition command
        Args:
            commandID: the command's ID
        Returns:
            Nothing
        """
        self.__removeImageCommand("ImageEditionCommand", commandID)
        
    def removeImageDeletionCommand(self, commandID):
        """
        Unregisters an image deletion command
        Args:
            commandID: the command's ID
        Returns:
            Nothing
        """
        self.__removeImageCommand("ImageDeletionCommand", commandID)
        
    def __removeImageCommand(self, tableName, commandID):
        update = "DELETE FROM {0} WHERE commandID = '{1}';".format(tableName, commandID)
        self._executeUpdate(update)
        
    def isImageEditionCommand(self, commandID):
        """
        Checks if a command is an image edition command or not.
        Args:
            commandID: the command's ID
        Returns:
            True if the command is an image edition command, and False otherwise.
        """
        return self.__classifyCommand("ImageEditionCommand", commandID)
    
    def isImageDeletionCommand(self, commandID):
        """
        Checks if a command is an image deletion command or not.
        Args:
            commandID: the command's ID
        Returns:
            True if the command is an image deletion command, and False otherwise.
        """
        return self.__classifyCommand("ImageDeletionCommand", commandID)
        
    def __classifyCommand(self, tableName, commandID):
        query = "SELECT * FROM {0} WHERE commandID = '{1}';".format(tableName, commandID)
        return self._executeQuery(query, True) != None
    
    def isBeingEdited(self, imageID):
        """
        Checks if an image is being edited
        Args:
            imageID: an image ID
        Returns:
            True if the image is being edited, and False otherwise 
        """
        return self.__isAffectedByCommand("ImageEditionCommand", imageID)
    
    def isBeingDeleted(self, imageID):
        """
        Checks if an image is being deleted
        Args:
            imageID: an image ID
        Returns:
            True if the image is being deleted, and False otherwise 
        """
        return self.__isAffectedByCommand("ImageDeletionCommand", imageID)
    
    def __isAffectedByCommand(self, tableName, imageID):
        query = "SELECT * FROM {0} WHERE imageID = {1}".format(tableName, imageID)
        return self._executeQuery(query, True) != None
    
    def getImageEditionCommandID(self, imageID):
        """
        Returns an image edition command's ID
        Args:
            imageID: the affected image's ID
        Returns:
            the image edition command's ID
        """
        return self.__getCommandID("ImageEditionCommand", imageID)
        
    def getImageDeletionCommandID(self, imageID):
        """
        Returns an image deletion command's ID
        Args:
            imageID: the affected image's ID
        Returns:
            the image deletion command's ID
        """
        return self.__getCommandID("ImageDeletionCommand", imageID)
    
    def __getCommandID(self, table, imageID):
        query = "SELECT commandID FROM {0} WHERE imageID = {1};".format(table, imageID)
        return self._executeQuery(query, True)    
    
    def changeImageCopiesState(self, imageID, state):
        """
        Updates an image's copies state
        Args:
            imageID: the image's ID
            state: the image copies' new state
        Returns:
            Nothing
        """
        update = "UPDATE ImageOnServer SET state = {1} WHERE imageId = {0}".format(imageID, state)
        self._executeUpdate(update)
        
    def changeImageCopyState(self, imageID, serverID, state):
        """
        Updates an image's copy state
        Args:
            imageID: the image's ID
            serverID: the ID of the virtual machine server where the image copy is deployed.
            state: the new state
        Returns:
            Nothing
        """
        update = "UPDATE ImageOnServer SET state = {2} WHERE imageId = {0} AND serverId = {1}".format(imageID, serverID, state)
        self._executeUpdate(update)      
        
    def isThereSomeImageCopyInState(self, imageID, state):
        """
        Checks if one or more copies of an image is in certain status
        Args:
            imageID: an image ID
            state: an image copy state
        Returns:
            True if one or more copies of an image is in the specified state, and False otherwise
        """
        query = "SELECT * FROM ImageOnServer WHERE imageID = {0} AND status = {1};".format(imageID, state)
        return self._executeQuery(query, True) != None
    
    def getHostedImagesInState(self, serverID, state):
        """
        Checks which of the hosted image copies are in the specified state
        Args:
            serverID: the host's ID
            state: an image copy state
        Returns: a list containing the IDs of the hosted image copies that are in the specified state
        """
        query = "SELECT imageId FROM ImageOnServer WHERE serverId = {0} AND state = {1};".format(serverID, state)
        result = self._executeQuery(query, False)
        if (result == None) : 
            return []
        else :
            return result
        
    def allocateVMServerResources(self, commandID, serverID, ramInUse, freeStorageSpace, freeTemporarySpace, activeVCPUs, activeHosts):
        """
        Allocates resources on a virtual machine server
        Args:
            commandID: a command ID
            serverID: the host's ID
            ramInUse: the allocated RAM
            freeStorageSpace: the allocated storage space
            freeTemporarySpace: the allocated temporary storage space
            activeVCPUs: the allocated VCPUs
            activeHosts: the allocated active hosts number
        Returns:
            Nothing
        """
        update = "INSERT INTO AllocatedVMServerResources VALUES('{0}', {1}, {2}, {3}, {4}, {5}, {6}, 0);"\
            .format(commandID, serverID, ramInUse, freeStorageSpace, freeTemporarySpace, activeVCPUs, activeHosts)
        self._executeUpdate(update)
        
    def freeVMServerResources(self, commandID, error):
        """
        Frees a part of the allocated resources on a virtual machine server
        Args:
            commandID: a command ID
            error: indicates if an error was detected while processing the command or not
        Returns:
            Nothing
        """
        if (error) :
            update = "DELETE FROM AllocatedVMServerResources WHERE commandID = '{0}';".format(commandID)
        else :
            update = "UPDATE AllocatedVMServerResources SET remove = 1 WHERE commandID = '{0}';".format(commandID)
        self._executeUpdate(update)
    
    def addAutoDeploymentCommand(self, commandID, imageID, remainingMessages):
        """
        Registers an auto-deployment command
        Args:
            commandID: the auto-deployment command's ID
            imageID: the affected image's ID
            remainingMesasges: the number of confirmation messages that are expected to be received from the virtual machine servers
        Returns:
            Nothing
        """
        update = "INSERT INTO AutoDeploymentCommand VALUES('{0}', {1}, {2}, 0)".format(commandID, imageID, remainingMessages)
        self._executeUpdate(update)
        
    def isAutoDeploymentCommand(self, commandID):
        """
        Checks if a command is an image auto-deployment command or not.
        Args:
            commandID: the command's ID
        Returns:
            True if the command is an image auto-deployment command, and False otherwise.
        """
        query = "SELECT * FROM AutoDeploymentCommand WHERE commandID = '{0}';".format(commandID)
        return self._executeQuery(query, True) != None
    
    def isAffectedByAutoDeploymentCommand(self, imageID):
        """
        Checks if a disk image is affected by an auto-deployment command
        Args:
            imageID: an image ID
        Returns:
            True if the image is affected by an auto-deployment command, and False if it's not
        """
        query = "SELECT * FROM AutoDeploymentCommand WHERE imageID = {0};".format(imageID)
        return self._executeQuery(query, True) != None
        
    def handleAutoDeploymentCommandOutput(self, commandID, error):
        """
        Handles an auto-deployment command confirmation message
        Args:
            commandID: the auto-deployment command's ID
            error: it's True when an error message was received, and False when an ordinary confirmation message
                was received
        Returns:
            Nothing
        """
        query = "SELECT remainingMessages, error FROM AutoDeploymentCommand WHERE commandID = '{0}';".format(commandID)
        result = self._executeQuery(query, True)
        generateOutputCommand = False
        if (result[0] == 1) :
            update = "DELETE FROM AutoDeploymentCommand WHERE commandID = '{0}';".format(commandID)
            generateOutputCommand = True
            error = result[1] != 0 or error
        else :
            if (error) : errorValue = 1
            else : errorValue = 0
            update = "UPDATE AutoDeploymentCommand SET remainingMessages = {1}, error = {2} WHERE commandID = '{0}';".format(commandID, result - 1, errorValue)
        self._executeUpdate(update)
        return (generateOutputCommand, error)
    
    def getAutoDeploymentCommandImageID(self, commandID):
        """
        Returns the identifier of the image affected by an auto-deployment command.
        Args:
            commandID: the auto-deployment command's ID
        Returns:
            the affected image's ID
        """
        query = "SELECT imageID FROM AutoDeploymentCommand WHERE commandID = '{0}';".format(commandID)
        return self._executeQuery(query, True)