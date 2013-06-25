# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: domainHandler.py    
    Version: 5.0
    Description: Domain handler
    
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

from virtualMachineServer.virtualNetwork.virtualNetworkManager import VirtualNetworkManager
from ccutils.processes.childProcessManager import ChildProcessManager
from virtualMachineServer.libvirtInteraction.libvirtConnector import LibvirtConnector
from virtualMachineServer.exceptions.vmServerException import VMServerException
from virtualMachineServer.libvirtInteraction.definitionFileEditor import DefinitionFileEditor
from virtualMachineServer.database.transfer_t import TRANSFER_T
from virtualMachineServer.libvirtInteraction.domainStartCallback import DomainStartCallback
from virtualMachineServer.libvirtInteraction.domainStopCallback import DomainStopCallback
from os import path, listdir

from time import sleep

class DomainHandler(DomainStartCallback, DomainStopCallback):
    """
    These objects interact with libvirt to handle domains.
    """    
    def __init__(self, dbConnector, vncServerIP, networkManager, packetManager, listenningPort, 
                 useQEMUWebsockets, websockifyPath, definitionFileDirectory,
                 sourceImageDirectory, executionImageDirectory, vncPasswordLength):
        """
        Initializes the domain handler's state
        Args:
            dbConnector: a database connector
            vncServerIP: the VNC server's IPv4 address
            networkManager: a network manager
            packetManager: a virtual machine server packet handler
            listenningPort: the control connection's port
            definitionFileDirectory: the directory where the definition files are
            sourceImageDirectory: the directory where the source disk images are
            executionImageDirectory: the directory where the active virtual machines' disk images are
            vncPasswordLength: the generated VNC password's length
        """
        self.__commandsDBConnector = dbConnector        
        self.__vncServerIP = vncServerIP
        self.__childProcessManager = ChildProcessManager()        
        self.__networkManager = networkManager
        self.__packetManager = packetManager
        self.__listenningPort = listenningPort
        self.__useQEMUWebsockets = useQEMUWebsockets
        self.__websockifyPath = websockifyPath
        self.__definitionFileDirectory = definitionFileDirectory
        self.__sourceImagePath = sourceImageDirectory
        self.__executionImagePath = executionImageDirectory
        self.__vncPasswordLength = vncPasswordLength
        self.__libvirtConnection = None
        self.__virtualNetworkManager = None
        self.__virtualNetworkName = None
    
    def connectToLibvirt(self, networkInterface, virtualNetworkName, gatewayIP, netmask, 
                         dhcpStartIP, dhcpEndIP, createVirtualNetworkAsRoot) :
        """
        Creates the libvirt connection and the virtual network
        Args:
            createVirtualNetworkAsRoot: indicates wether the virtual network must be
                created as the super-user or not. This is required in some systems.
        Returns:
            Nothing
        """
        self.__libvirtConnection = LibvirtConnector(LibvirtConnector.KVM, self, self)
        self.__virtualNetworkManager = VirtualNetworkManager(createVirtualNetworkAsRoot)
        self.__virtualNetworkManager.createVirtualNetwork(virtualNetworkName, gatewayIP, 
                                                          netmask, dhcpStartIP, 
                                                          dhcpEndIP)
        self.__virtualNetworkName = virtualNetworkName
    
    def doInitialCleanup(self):
        """
        Does the initial cleanup, freeing the unused resources assigned to the
            registered virtual machines.
        Args:
            None
        Returns:
            Nothing
        """
        activeDomainNames = self.__libvirtConnection.getActiveDomainNames()
        registeredDomainNames = self.__commandsDBConnector.getRegisteredDomainNames()
        for domainName in registeredDomainNames :
            if (not domainName in activeDomainNames) :
                self.__freeDomainResources(domainName)
        self.__commandsDBConnector.allocateAssignedMACsUUIDsAndVNCPorts()
        
    def shutdown(self, timeout):
        """
        Destroys all the domains.
        Args:
            timeout: the number of seconds to wait before destruction all the domains.
        Returns:
            Nothing
        """
        if (self.__libvirtConnection != None) :
            if (timeout == 0) :
                self.__libvirtConnection.destroyAllDomains()
            else :
                self.__waitForDomainsToTerminate(timeout)
        try :
            self.__virtualNetworkManager.destroyVirtualNetwork(self.__virtualNetworkName)  
        except Exception:
            pass
        self.__childProcessManager.waitForBackgroundChildrenToTerminate()
        
    def createDomain(self, imageID, userID, commandID):
        """
        Creates a domain
        Args:
            imageID: the image to use's ID
            userID: the domain owner's ID
            commandID: the domain boot command's ID
        Returns:
            Nothing
        """    
        
        try : 
            diskImagesCreated = False
            websockifyPID = -1       
            imageFound = False
            newUUID = None
            newMAC = None
            
            definitionFile = self.__definitionFileDirectory + self.__commandsDBConnector.getDefinitionFilePath(imageID)
            originalName = "{0}_".format(imageID)
            dataImagePath = self.__commandsDBConnector.getDataImagePath(imageID)
            osImagePath = self.__commandsDBConnector.getOSImagePath(imageID)
            isBootable = self.__commandsDBConnector.getBootableFlag(imageID)        
            imageFound = True
            
            # Generate the configuration parameters
            newUUID, newMAC = self.__commandsDBConnector.extractFreeMACAndUUID()
            newPort = self.__commandsDBConnector.extractFreeVNCPort()
            newName = originalName + str(newPort)        
            newPassword = self.__generateVNCPassword()
            sourceOSDisk = self.__sourceImagePath + osImagePath               
            
            if(isBootable):                           
                # Create the disk images in copy-on-write mode
                trimmedDataImagePath = dataImagePath
                try:
                    trimmedDataImagePath = dataImagePath[0:dataImagePath.index(".qcow2")]
                except:
                    pass
                trimmedOSImagePath = osImagePath
                try:
                    trimmedOSImagePath = osImagePath[0:osImagePath.index(".qcow2")]
                except:
                    pass   
                
                newDataDisk = self.__executionImagePath + trimmedDataImagePath + str(newPort) + ".qcow2"
                newOSDisk = self.__executionImagePath + trimmedOSImagePath + str(newPort) + ".qcow2"                
               
                # If one of the files already exist, we'll get rid of it.
                if (path.exists(newDataDisk)):
                    print("Warning: the file " + newDataDisk + " already exists")
                    ChildProcessManager.runCommandInForeground("rm " + newDataDisk, VMServerException)
                    
                if (path.exists(newOSDisk)):
                    print("Warning: the file " + newOSDisk + " already exists")
                    ChildProcessManager.runCommandInForeground("rm " + newOSDisk, VMServerException)
                    
                try :
                    ChildProcessManager.runCommandInForeground("cd " + self.__sourceImagePath + ";" + "cp --parents "+ dataImagePath + " " + self.__executionImagePath, VMServerException)
                    ChildProcessManager.runCommandInForeground("mv " + self.__executionImagePath + dataImagePath +" " + newDataDisk, VMServerException)
                    ChildProcessManager.runCommandInForeground("qemu-img create -b " + sourceOSDisk + " -f qcow2 " + newOSDisk, VMServerException)
                except Exception as e:
                    diskImagesCreated = True
                    raise e
            
            else :
                # The images will not be created in copy-on-write mode. In fact, their stored copies will be
                # modified (we're editing them)
                newDataDisk = path.join(self.__sourceImagePath, dataImagePath)
                newOSDisk = path.join(self.__sourceImagePath, osImagePath)            
            
            # Build dthe definition file
            xmlFile = DefinitionFileEditor(definitionFile)
            xmlFile.setDomainIdentifiers(newName, newUUID)
            xmlFile.setImagePaths(newOSDisk, newDataDisk)            
            xmlFile.setVirtualNetworkConfiguration(self.__virtualNetworkName, newMAC)
            xmlFile.setVNCServerConfiguration(self.__vncServerIP, newPort, newPassword, self.__useQEMUWebsockets)
            
            string = xmlFile.generateConfigurationString()        
            # Start the domain
            self.__libvirtConnection.startDomain(string)
            
            if (not self.__useQEMUWebsockets) :
                websockifyPID = self.__childProcessManager.runCommandInBackground([self.__websockifyPath,
                                            self.__vncServerIP + ":" + str(newPort + 1),
                                            self.__vncServerIP + ":" + str(newPort)])
            
            # Everything went OK => register the resources on the database
        
            self.__commandsDBConnector.registerVMResources(newName, imageID, newPort, newPassword, userID, websockifyPID, newOSDisk,  newDataDisk, newMAC, newUUID)
            self.__commandsDBConnector.addVMBootCommand(newName, commandID)
       
        except Exception:
            # Free the allocated resources, generate an error packet and send it.
            if (imageFound and not isBootable) :                
                self.__commandsDBConnector.deleteImage(imageID)
            if (newUUID != None) :
                self.__commandsDBConnector.freeMACAndUUID(newUUID, newMAC)
            if (diskImagesCreated) :
                ChildProcessManager.runCommandInForeground("rm -rf " + path.dirname(newOSDisk), None)
            if (websockifyPID != -1) :
                ChildProcessManager.runCommandInForeground("kill " + websockifyPID, None)
            p = self.__packetManager.createInternalErrorPacket(commandID)
            self.__networkManager.sendPacket('', self.__listenningPort, p)
            

        
    def destroyDomain(self, domainUID):
        """
        Destroys a domain
        Args:
            domainUID: the domain to destroy's unique identifier
        Returns:
            Nothing
        """
        domainName = self.__commandsDBConnector.getDomainNameFromVMBootCommand(domainUID)
        if (domainName == None) :
            # Ignoramos la petición: el dominio ya está apagado
            return
        bootableFlag = self.__commandsDBConnector.getBootableFlag(self.__commandsDBConnector.getDomainImageID(domainName))
        if (bootableFlag) :
            self.__libvirtConnection.destroyDomain(domainName)
        else:
            self.__libvirtConnection.shutdownDomain(domainName)
            
    def rebootDomain(self, domainUID):
        """
        Reboots a domain
        Args:
            domainUID: the domain to reboot's unique identifier
        Returns:
            Nothing
        """
        domainName = self.__commandsDBConnector.getDomainNameFromVMBootCommand(domainUID)
        if (domainName == None) :
            # Ignoramos la petición: el dominio ya está apagado
            return
        self.__libvirtConnection.rebootDomain(domainName)
        
    def _onDomainStart(self, domain):
        """
        This method will be called to handle a domain creation event.
        Args:
            domain: an object containing the domain's data
        Returns:
            Nothing
        """
        self.__sendConnectionData(domain)
        
    def __sendConnectionData(self, domainInfo):
        """
        Sends a domain's connection data
        Args:
            domainInfo: an object containing the domain's data
        Returns:
            Nothing
        """
        ip = domainInfo["VNCip"]
        port = domainInfo["VNCport"]
        password = domainInfo["VNCpassword"]
        domainName = domainInfo["name"]
        commandID = None
        while (commandID == None) :
            commandID = self.__commandsDBConnector.getVMBootCommand(domainName)
            if (commandID == None) :
                sleep(0.1)
        packet = self.__packetManager.createVMConnectionParametersPacket(ip, port + 1, password, commandID)
        self.__networkManager.sendPacket('', self.__listenningPort, packet)
        
    def _onDomainStop(self, domainName):
        """
        This method will be called to handle a domain stop event.
        Args:
            domainName: the stopped domain's name
        Returns:
            Nothing
        """
        if (self.__commandsDBConnector.getVMBootCommand(domainName) != None) :            
            self.__freeDomainResources(domainName)
            
    def __freeDomainResources(self, domainName, deleteDiskImages=True):
        """
        Free the resources assigned to a domain
        Args:
            domainName: a domain name
            deleteDiskImages: indicates wether the disk images must be deleted or not
        Returns:
            Nothing
        """
        dataImagePath = self.__commandsDBConnector.getDomainDataImagePath(domainName)
        osImagePath = self.__commandsDBConnector.getDomainOSImagePath(domainName)
        imageID = self.__commandsDBConnector.getDomainImageID(domainName)
        websockify_pid = self.__commandsDBConnector.getWebsockifyDaemonPID(domainName)
        isBootable = self.__commandsDBConnector.getBootableFlag(imageID)        
        commandID = self.__commandsDBConnector.getVMBootCommand(domainName)
        
        self.__commandsDBConnector.unregisterDomainResources(domainName)     
        
        if (websockify_pid != -1) :
            ChildProcessManager.runCommandInForeground("kill -s TERM " + str(websockify_pid), None)   
        
        if isBootable :
            # If the domain was manually stopped, libvirt has already got rid of the disk images.
            # ==> we don't have to complain if we can't find them
            ChildProcessManager.runCommandInForeground("rm " + dataImagePath, None)
            ChildProcessManager.runCommandInForeground("rm " + osImagePath, None)
            dataDirectory = path.dirname(dataImagePath)
            osDirectory = path.dirname(osImagePath)
            if (path.exists(dataDirectory) and listdir(dataDirectory) == []) :
                ChildProcessManager.runCommandInForeground("rm -rf " + dataDirectory, None)
            if (osDirectory != dataDirectory and path.exists(osDirectory) and listdir(osDirectory) == []) :
                ChildProcessManager.runCommandInForeground("rm -rf " + osDirectory, None)            
                    
        else :
            data = dict()            
            connectionData = self.__commandsDBConnector.getImageRepositoryConnectionData(commandID)
            data["Transfer_Type"] = TRANSFER_T.STORE_IMAGE
            data["DataImagePath"] = dataImagePath
            data["OSImagePath"] = osImagePath
            data["DefinitionFilePath"] = self.__commandsDBConnector.getDefinitionFilePath(imageID)
            data["RepositoryIP"] = connectionData["RepositoryIP"]
            data["RepositoryPort"] = connectionData["RepositoryPort"]
            data["CommandID"] = commandID            
            data["TargetImageID"] = imageID
            self.__commandsDBConnector.addToCompressionQueue(data)
            self.__commandsDBConnector.removeImageRepositoryConnectionData(commandID)
            self.__commandsDBConnector.deleteImage(imageID)              
    
    def __waitForDomainsToTerminate(self, timeout):
        """
        Waits until all the active domains have finished, stopping at timeout seconds.
        Args:
            timeout: a timeout in seconds
        Returns:
            Nothing
        """
        wait_time = 0
        while (self.__libvirtConnection.getNumberOfDomains() != 0 and wait_time < timeout) :
            sleep(0.5)
            wait_time += 0.5
            
    def __generateVNCPassword(self):
        """
        Generates a VNC random password
        Args:
            None
        Returns:
            a string containing the generated password
        """
        return ChildProcessManager.runCommandInForeground("openssl rand -base64 " + str(self.__vncPasswordLength), VMServerException)
    
    def getLibvirtStatusData(self):
        """
        Returns libvirt's status data.
        Args:
            None
        Returns:
            A dictionary containing libvirt's status data.
        """
        return self.__libvirtConnection.getStatusData()