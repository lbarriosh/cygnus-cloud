# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: clusterConnector.py    
    Version: 5.0
    Description: cluster connector definitions
    
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
from clusterEndpoint.databases.minimalClusterEndpointDBConnector import MinimalClusterEndpointDBConnector
from clusterEndpoint.databases.commandsDatabaseConnector import CommandsDatabaseConnector
from clusterEndpoint.commands.commandsHandler import CommandsHandler
from clusterEndpoint.codes.spanishCodesTranslator import SpanishCodesTranslator
from time import sleep

class ClusterConnector(object):
    """
    These objects will be used by the web application to interact with the infrastructure
    @attention: DO NOT rely on the command IDs internal representation: it may change without prior notice.
    """
    
    def __init__(self, userID):
        """
        Initializes the connector's state
        Args:
            userID: el identificador del usuario que accede al sistema. Se trata de un entero.
        """
        self.__userID = userID
        self.__commandsHandler = CommandsHandler(SpanishCodesTranslator())
    
    def connectToDatabases(self, endpointDBName, commandsDBName, databaseUser, databasePassword):
        """
        Establishes the database connections
        Args:
            endpointDBName: the cluster endpoint database's name
            commandsDBName: the commands database's name
            databaseUser: the web application database user
            databasePassword: the web application database user password
        Returns:
            Nothing
        """
        self.__endpointDBConnector = MinimalClusterEndpointDBConnector(databaseUser, databasePassword, endpointDBName)
        self.__commandsDBConnector = CommandsDatabaseConnector(databaseUser, databasePassword, commandsDBName, 1)    
        
    def dispose(self):
        """
        Closes the databse connections
        Args:
            None
        Returns:
            Nothing
        """
        pass
        
    def getActiveVMsData(self, showAllVMs=False, showEditionVMs=False):
        """
        Returns the active virtual machine's data
        Argumentos:
            ownerID: the virtual machines' owner. If it's None, all the active virtual machines' VNC data
            will be returned
            show_edited: if it's True, the edition virtual machines data will also be returned.
        Returns:
            a list of dictionaries. Each one contains an active virtual machine's VNC data
        """
        if not showAllVMs :
            userID = self.__userID
        else :
            userID = None
        return self.__endpointDBConnector.getActiveVMsVNCData(userID, showEditionVMs)
    
    def getVMDistributionData(self):
        """
        Returns all the image copies distribution.
        Args:
            None
        Returns:
            a list of dictionaries. Each one contains an image location's data.
        """
        return self.__endpointDBConnector.getImageCopiesDistributionData()
        
    def getVMServersData(self):
        """
        Returns all the virtual machine servers configuration
        Args:
            None
        Returns:
            a list of dictionaries. Each one contains a virtual machine server's configuration.
        """
        return self.__endpointDBConnector.getVMServersConfiguration()
        
    def registerVMServer(self, vmServerIP, vmServerPort, vmServerName, isEditionServer):
        """
        Registers a virtual machine server
        Args:
            vmServerIP: the new virtual machine server's IP address
            vmServerPort: the new virtual machine server's listenning port
            vmServerName: the new virtual machine server's name
            isEditionServer: indicates if the virtual machine server will be used to create and edit 
                images or not
        Returns:
            a command ID
        """
        (commandType, commandArgs) = self.__commandsHandler.createVMServerRegistrationCommand(vmServerIP, vmServerPort, vmServerName, isEditionServer)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
        
    def unregisterVMServer(self, vmServerNameOrIP, halt):
        """
        Unregisters a virtual machine server
        Args:
            unregister: if it's True, an virtual machine server unregistration command will be created. If it's False,
                a virtual machine server shutdown command will be created.
            vmServerNameOrIPAddress: the virtual machine server's name or IPv4 address
            halt: indicates if the virtual machines must be immediately shut down or not
        Returns:
            a command ID
        """
        (commandType, commandArgs) = self.__commandsHandler.createVMServerUnregistrationOrShutdownCommand(True, vmServerNameOrIP, halt)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def shutdownVMServer(self, vmServerNameOrIP, haltVMs):
        """
        Shuts down a virtual machine server
        Args:
            vmServerNameOrIPAddress: the virtual machine server's name or IPv4 address
            haltVMs: indicates if the virtual machines must be immediately shut down or not
        Returns:
            a command ID
        """
        (commandType, commandArgs) = self.__commandsHandler.createVMServerUnregistrationOrShutdownCommand(False, vmServerNameOrIP, haltVMs)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def bootUpVMServer(self, vmServerNameOrIP):
        """
        Boots up a virtual machine server
        Args:
            vmServerNameOrIP: the virtual machine server's name or IP address
        Returns:
            a command ID
        """
        (commandType, commandArgs) = self.__commandsHandler.createVMServerBootCommand(vmServerNameOrIP)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def bootUpVM(self, imageID):
        """
        Boots up a virtual machine
        Args:
            imageID: an image ID
        Returns:
            a command ID
        """
        (commandType, commandArgs) = self.__commandsHandler.createVMBootCommand(imageID, self.__userID)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def shutDownInfrastructure(self, haltVMServers):
        """
        Shuts down all the infrastructure machines.
        Args:
            haltServers: indicates if the virtual machine servers must be shut down immediately or not.
        Returns: 
            a command ID
        """
        (commandType, commandArgs) = self.__commandsHandler.createHaltCommand(haltVMServers)
        self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
        
    def destroyDomain(self, domainID):
        """
        Destroys a virtual machine
        Args:
            domainID: the domain to be destructed ID
        Devuelve:
            a command ID
        """
        (commandType, commandArgs) = self.__commandsHandler.createDomainDestructionCommand(domainID)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def rebootDomain(self, domainID):
        """
        Reboots a virtual machine
        Args:
            domainID: the domain to be rebooted ID
        Devuelve:
            a command ID
        """
        (commandType, commandArgs) = self.__commandsHandler.createDomainRebootCommand(domainID)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def deployImage(self, serverNameOrIPAddress, imageID):
        """
        Deploys an image in a virtual machine server
        Args:
            serverNameOrIPAddress: the host's name or IP address
            imageID: the affected image's ID
        Returns:
            a command ID
        """
        (commandType, commandArgs) = self.__commandsHandler.createImageDeploymentCommand(True, serverNameOrIPAddress, imageID)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def deleteImage(self, serverNameOrIPAddress, imageID):
        """
        Deletes an image from a virtual machine server
        Args:
            serverNameOrIPAddress: the host's name or IP address
            imageID: the affected image's ID
        Returns:
            a command ID
        """
        (commandType, commandArgs) = self.__commandsHandler.createImageDeploymentCommand(False, serverNameOrIPAddress, imageID)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def createImage(self, baseImageID, imageName, imageDescription):
        """
        Creates a new image
        Args:
            baseImageID: the base image's ID
            imageName: the new image's name
            imageDescription: the new image's description
        Returns:
            a command ID
        """
        (commandType, commandArgs) = self.__commandsHandler.createImageAdditionCommand(self.__userID, baseImageID, imageName, imageDescription)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def editImage(self, imageID):
        """
        Edits an existing image
        Args:
            imageID: the affected image's ID
        Returns:
            a command ID
        """
        if (isinstance(imageID, str)) :
            imageID = self.__endpointDBConnector.getImageID(imageID)
        (commandType, commandArgs) = self.__commandsHandler.createImageEditionCommand(imageID, self.__userID)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def deleteImageFromInfrastructure(self, imageID):
        """
        Deletes an image from the infrastructure
        Args:
            imageID: the affected image's ID
        Returns:
            a command ID
        """
        (commandType, commandArgs) = self.__commandsHandler.createDeleteImageFromInfrastructureCommand(imageID)        
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def deployEditedImage(self, temporaryID):
        """
        Deploys an edited image
        Args:
            temporaryID: a temporary ID
        Returns:
            a command ID
        """
        imageID = self.__endpointDBConnector.getImageData(temporaryID)["ImageID"]
        (commandType, commandArgs) = self.__commandsHandler.createAutoDeploymentCommand(imageID, -1)
        l = temporaryID.split("|")
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs, float(l[1]))
    
    def deployNewImage(self, temporaryID, max_instances):
        """"
        Deploys a new image
        Args:
            temporaryID: a temporary ID
            max_instances: the maximum instance number
        Returns:
            a command ID
        """
        imageID = self.__endpointDBConnector.getImageData(temporaryID)["ImageID"]
        (commandType, commandArgs) = self.__commandsHandler.createAutoDeploymentCommand(imageID, max_instances)
        l = temporaryID.split("|")
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs, float(l[1]))
    
    def autoDeployImage(self, imageID, instances):
        """
        Performs an automatic image deployment operation
        Args:
            imageID: the affected image's ID
            max_instances: the maximum new instance number
        Returns:
            a command ID
        """
        (commandType, commandArgs) = self.__commandsHandler.createAutoDeploymentCommand(imageID, instances)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def changeVMServerConfiguration(self, serverNameOrIPAddress, newName, newIPAddress, newPort, 
                                    newImageEditionBehavior):
        """
        Modifies a virtual machine server's configuration
        Args:
            serverNameOrIPAddress: the virtual machine server's name or IP address
            newName: the virtual machine server's new name
            newIPAddress: the virtual machine server's IP new address
            newPort: the virtual machine server's new port            
            newImageEditionBehavior: indicates if the virtual machine server will be used to create and edit 
                images or not
        Returns:
            a command ID
        """
        (commandType, commandArgs) = self.__commandsHandler.createVMServerConfigurationChangeCommand(serverNameOrIPAddress, 
            newName, newIPAddress, newPort, newImageEditionBehavior)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def getCommandOutput(self, commandID):
        """
        Returns a command's output
        Args:
            commandID: the command's ID
        Returns:
            - an empty tuple if the command is still running, or
            - a dictionary containing its output if it's not
        """
        if (self.__commandsDBConnector.isRunning(commandID)) :
            return ()
        else :
            result = self.__commandsDBConnector.getCommandOutput(commandID)
            if (result != None) :
                (outputType, outputContent) = result
                result = self.__commandsHandler.deserializeCommandOutput(outputType, outputContent)
            return result
    
    def waitForCommandOutput(self, commandID):
        """
        Returns a command's output. This is a blocking operation.
        Args:
            commandID: the command's ID
        Returns: 
            - None if the command has no output, or
            - a dictionary containing the command's output if it's not.
        """
        while (self.__commandsDBConnector.isRunning(commandID)) :
                sleep(0.5)
        result = self.__commandsDBConnector.getCommandOutput(commandID)
        if result == None :
            return None
        else :
            return self.__commandsHandler.deserializeCommandOutput(result[0], result[1])
        
    def getBootableImagesData(self, imageIDs):
        """
        Returns the bootable image data
        Args:
            imageID: a list of image identifiers. If it's not empty, it will be used
            to filter the query results.
        Returns:
            A list of dictionaries. Each one contains a bootable image's data.
        """
        return self.__endpointDBConnector.getBootableImagesData(imageIDs)
    
    def getBaseImagesData(self):
        """
        Returns the base images data
        Args:
            None
        Returns: 
             A list of dictionaries. Each one contains a base image's data.
        """
        return self.__endpointDBConnector.getBaseImagesData()
        
    def getEditedImageIDs(self, userID):
        """
        Returns the edited images temporary IDs
        Args:
            userID: a user ID. If it's none, all the edited images' IDs will be returned
        Returns:
            a list containing the edited images' temporary IDs.
        """
        return self.__endpointDBConnector.getEditedImageIDs(userID)
    
    def getVanillaImageFamilyID(self, imageID):
        """
        Returns the virtual machine family ID associated with an image.
        Args:
            imageID: an image ID
        Returns:
            the virtual machine family ID associated with the given image.
        """
        return self.__endpointDBConnector.getVMFamilyID(imageID)
    
    def getVanillaImageFamilyData(self, vanillaImageFamilyID):
        """
        Returns a virtual machine family data
        Args:
            vmFamilyID: a virtual machine family ID
        Returns:
            A dictionary containing the virtual machine family's data
        """
        return self.__endpointDBConnector.getVMFamilyData(vanillaImageFamilyID)
    
    def getMaxVanillaImageFamilyData(self):
        """
        Returns the most powerful virtual machine family data
        Args:
            None
        Returns:
            A dictionary containing the most powerful virtual machine family data
        """
        return self.__endpointDBConnector.getMaxVMFamilyData()
    
    def getImageRepositoryStatus(self):
        """
        Returns the image repository current status
        Args:
            None
        Returns:
            A dictionary containing the image repository current status
        """
        return self.__endpointDBConnector.getImageRepositoryStatus()
    
    def getVirtualMachineServerStatus(self, serverName):
        """
        Returns a virtual machine server's status
        Args:
            A virtual machine server's name
        Returns:
            a dictionary containing the virtual machine server's status
        """
        return self.__endpointDBConnector.getVirtualMachineServerStatus(serverName)
    
    def getOSTypes(self):
        """
        Returns the registered OS types
        Args:
            None
        Returns:
            a list of dictionaries. Each one contains one of the registered OS types data.
        """
        return self.__endpointDBConnector.getOSTypes()
    
    def getOSTypeVariants(self,familyID):
        """
        Returns the registered OS variants
        Args:
            None
        Returns:
            a list of dictionaries. Each one contains one of the registered OS variantas data.
        """
        return self.__endpointDBConnector.getOSTypeVariants(familyID)
    
    def getImageData(self, imageID):
        """
        Returns an image's data
        Args:
            imageID: a permanent or a temporary image ID
        Returns:
            a dictionary containing the image's data
        """
        return self.__endpointDBConnector.getImageData(imageID)        
    
    def getPendingNotifications(self):
        """
        Returns the user's pending notifications
        Args:
            None
        Returns:
            A list of strings containing the user's pending notifications.
        """
        return self.__commandsDBConnector.getPendingNotifications(self.__userID)
        
    def countPendingNotifications(self):
        """
        Counts the user's pending notifications
        Args:
            None
        Returns:
            the user's pending notification number
        """
        return self.__commandsDBConnector.countPendingNotifications(self.__userID)
    
if __name__ == "__main__" :
    connector = ClusterConnector(1)
    connector.connectToDatabases("ClusterEndpointDB", "CommandsDB", "website_user", "CygnusCloud")
    commandID = connector.destroyDomain("1|1372178498.7")