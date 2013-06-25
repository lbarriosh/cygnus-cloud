# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: vmServerReactor.py    
    Version: 5.0
    Description: virtual machine server packet reactor definitions
    
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

from network.manager.networkManager import NetworkManager, NetworkCallback
from virtualMachineServer.packetHandling.packet_t import VM_SERVER_PACKET_T
from virtualMachineServer.packetHandling.packetHandler import VMServerPacketHandler
from virtualMachineServer.database.vmServerDB import VMServerDBConnector
from virtualMachineServer.database.transfer_t import TRANSFER_T
from virtualMachineServer.threads.fileTransferThread import FileTransferThread
from virtualMachineServer.threads.compressionThread import CompressionThread
from virtualMachineServer.exceptions.vmServerException import VMServerException
from virtualMachineServer.libvirtInteraction.domainHandler import DomainHandler
from ccutils.processes.childProcessManager import ChildProcessManager
from network.interfaces.ipAddresses import get_ip_address 
import os
import multiprocessing
import sys
import re
from math import ceil
from errors.codes import ERROR_DESC_T

class VMServerReactor(NetworkCallback):
    """
    Virtual machine server packet reactor
    """
    def __init__(self, configurationFileParser):
        """
        Initializes the reactor's state, establishes the connection with the database
        and creates the control connection
        Args:
            configurationFileParser: the virtual machine server's configuration file parser
        """        
        self.__finished = False
        self.__emergencyStop = False
        self.__fileTransferThread = None
        self.__compressionThread = None
        self.__networkManager = None
        self.__parser = configurationFileParser
        self.__domainHandler = None
        self.__domainTimeout = 0
        try :
            self.__connectToDatabases("VMServerDB", self.__parser.getConfigurationParameter("databaseUserName"), 
                                      self.__parser.getConfigurationParameter("databasePassword"))
            self.__startListenning()
        except Exception as e:
            print e.message
            self.__emergencyStop = True
            self.__finished = True
        
    def __connectToDatabases(self, databaseName, user, password) :
        """
        Establishes the connection with the database
        Args:
            databaseName: a database name
            user: a SQL username
            password: the user's password
        Returns:
            Nothing
        """
        self.__dbConnector = VMServerDBConnector(user, password, databaseName)  
            
    def __startListenning(self):
        """
        Creates the control connection
        Args:
            None
        Returns:
            Nothing
        """    
        networkInterface = self.__parser.getConfigurationParameter("vncNetworkInterface")
        listenningPort = self.__parser.getConfigurationParameter("listenningPort")
        try :
            self.__vncServerIP = get_ip_address(networkInterface)
        except Exception :
            raise Exception("Error: the network interface '{0}' is not ready. Exiting now".format(networkInterface))    
        self.__ftpTimeout = self.__parser.getConfigurationParameter("FTPTimeout")
        self.__listenningPort = listenningPort
        self.__networkManager = NetworkManager(self.__parser.getConfigurationParameter("certificatePath"))
        self.__networkManager.startNetworkService()
        self.__useSSL = self.__parser.getConfigurationParameter("useSSL")
        self.__packetManager = VMServerPacketHandler(self.__networkManager)            
        self.__connectToDatabases("VMServerDB", self.__parser.getConfigurationParameter("databaseUserName"), self.__parser.getConfigurationParameter("databasePassword"))
            
        self.__domainHandler = DomainHandler(self.__dbConnector, self.__vncServerIP, self.__networkManager, self.__packetManager, self.__listenningPort, 
                                                 self.__parser.getConfigurationParameter("useQEMUWebsockets"),
                                                 self.__parser.getConfigurationParameter("websockifyPath"),
                                                 self.__parser.getConfigurationParameter("configFilePath"),
                                                 self.__parser.getConfigurationParameter("sourceImagePath"), self.__parser.getConfigurationParameter("executionImagePath"),
                                                 self.__parser.getConfigurationParameter("passwordLength"))
        self.__domainHandler.connectToLibvirt(self.__parser.getConfigurationParameter("vncNetworkInterface"), 
                                                  self.__parser.getConfigurationParameter("vnName"), self.__parser.getConfigurationParameter("gatewayIP"), 
                                                  self.__parser.getConfigurationParameter("netMask"), self.__parser.getConfigurationParameter("dhcpStartIP"), 
                                                  self.__parser.getConfigurationParameter("dhcpEndIP"), self.__parser.getConfigurationParameter("createVirtualNetworkAsRoot"))
            
        self.__domainHandler.doInitialCleanup()
        self.__deleteTemporaryZipFiles()
        self.__fileTransferThread = FileTransferThread(self.__networkManager, self.__listenningPort, self.__packetManager,
                                                       self.__parser.getConfigurationParameter("TransferDirectory"),
                                                       self.__parser.getConfigurationParameter("FTPTimeout"), 
                                                       self.__parser.getConfigurationParameter("MaxTransferAttempts"), self.__dbConnector, self.__useSSL)
        self.__compressionThread = CompressionThread(self.__parser.getConfigurationParameter("TransferDirectory"), self.__parser.getConfigurationParameter("sourceImagePath"),
                                                     self.__parser.getConfigurationParameter("configFilePath"),
                                                     self.__dbConnector, self.__domainHandler, self.__networkManager, self.__listenningPort, self.__packetManager)
        self.__fileTransferThread.start()
        self.__compressionThread.start()
        self.__networkManager.listenIn(self.__listenningPort, self, self.__useSSL)
        
    def __deleteTemporaryZipFiles(self):
        """
        Deletes the temporary zip files
        Args:
            None
        Returns:
            Nothing
        """
        transfer_dir_path = self.__parser.getConfigurationParameter("TransferDirectory")
        for filePath in os.listdir(transfer_dir_path) :
            fileName = os.path.splitext(filePath)[0]
            if re.match("[^0-9]", fileName):
                # The non-temporary zip files only have numbers on their names
                os.remove(os.path.join(transfer_dir_path, filePath))
    
    def shutdown(self):
        """
        Shuts down the virtual machine server
        Args:
            None
        Returns:
            Nothing
        """                
            
        if (self.__emergencyStop) :            
            self.__domainTimeout = 0
            
        self.__domainHandler.shutdown(self.__domainTimeout)                   
        
        if (self.__fileTransferThread != None) :
            self.__fileTransferThread.stop()
            self.__fileTransferThread.join()
        if (self.__compressionThread != None) :
            self.__compressionThread.stop()
            self.__compressionThread.join()
            
        if (self.__networkManager != None) :
            self.__networkManager.stopNetworkService() # Dejar de atender peticiones inmediatamente
        sys.exit()              
        
    def processPacket(self, packet):
        """
        Processes a packet sent from the cluster server
        Args:
            packet: the packet to process
        Returns:
            Nothing
        """
        data = self.__packetManager.readPacket(packet)
        if (data["packet_type"] == VM_SERVER_PACKET_T.CREATE_DOMAIN) :
            self.__domainHandler.createDomain(data["MachineID"], data["UserID"], data["CommandID"])
        elif (data["packet_type"] == VM_SERVER_PACKET_T.SERVER_STATUS_REQUEST) :
            self.__sendStatusData()
        elif (data["packet_type"] == VM_SERVER_PACKET_T.USER_FRIENDLY_SHUTDOWN) :
            self.__domainTimeout = data["Timeout"]
            self.__finished = True
        elif (data["packet_type"] == VM_SERVER_PACKET_T.HALT) :
            self.__domainTimeout = 0
            self.__finished = True
        elif (data['packet_type'] == VM_SERVER_PACKET_T.QUERY_ACTIVE_VM_DATA) :
            self.__sendDomainsVNCConnectionData()
        elif (data['packet_type'] == VM_SERVER_PACKET_T.DESTROY_DOMAIN) :
            self.__domainHandler.destroyDomain(data["DomainID"])
        elif (data['packet_type'] == VM_SERVER_PACKET_T.REBOOT_DOMAIN) :
            self.__domainHandler.rebootDomain(data["DomainID"])
        elif (data['packet_type'] == VM_SERVER_PACKET_T.QUERY_ACTIVE_DOMAIN_UIDS) :
            self.__sendActiveDomainUIDs()
        elif (data['packet_type'] == VM_SERVER_PACKET_T.IMAGE_EDITION) :
            self.__processImageEditionPacket(data)
        elif (data['packet_type'] == VM_SERVER_PACKET_T.DEPLOY_IMAGE) :
            self.__processDeployImagePacket(data)
        elif (data['packet_type'] == VM_SERVER_PACKET_T.DELETE_IMAGE) :
            self.__processDeleteImagePacket(data)
            
    def __processDeployImagePacket(self, data):
        """
        Processes an image deployment packet
        Args:
            data: a dictionary containing the packet to process' data
        Returns:
            Nothing
        """
        data.pop("packet_type")
        data["Transfer_Type"] = TRANSFER_T.DEPLOY_IMAGE
        self.__dbConnector.addToTransferQueue(data)
        
    def __processDeleteImagePacket(self, data):
        
        isBootable = self.__dbConnector.getBootableFlag(data["ImageID"])
        
        if(isBootable):            
            osImagePath = os.path.join(self.__parser.getConfigurationParameter("sourceImagePath") 
                                   ,self.__dbConnector.getOSImagePath(data["ImageID"]))
            definitionFilePath = os.path.join(self.__parser.getConfigurationParameter("configFilePath") 
                                   ,self.__dbConnector.getDefinitionFilePath(data["ImageID"]))
            
            try :
                
                self.__dbConnector.deleteImage(data["ImageID"])                
                ChildProcessManager.runCommandInForeground("rm -rf " + os.path.dirname(osImagePath), VMServerException)                
                ChildProcessManager.runCommandInForeground("rm -rf " + os.path.dirname(definitionFilePath), VMServerException)
                p = self.__packetManager.createConfirmationPacket(VM_SERVER_PACKET_T.IMAGE_DELETED, data["ImageID"], data["CommandID"])
            except Exception:
                p = self.__packetManager.createErrorPacket(VM_SERVER_PACKET_T.IMAGE_DELETION_ERROR, ERROR_DESC_T.VM_SRVR_INTERNAL_ERROR, 
                                                            data["CommandID"])                
            
        else:
            if (isBootable != None) :
                errorCode = ERROR_DESC_T.VMSRVR_LOCKED_IMAGE
            else :
                errorCode = ERROR_DESC_T.VMSRVR_UNKNOWN_IMAGE
            
            p = self.__packetManager.createErrorPacket(VM_SERVER_PACKET_T.IMAGE_DELETION_ERROR, errorCode, 
                                                       data["CommandID"])
        
        self.__networkManager.sendPacket('', self.__listenningPort, p)
            
        
        
    def __processImageEditionPacket(self, data):
        """
        Processes an image edition packet
        Args:
            data: a dictionary containing the packet to process' data
        Returns:
            Nothing
        """
        data.pop("packet_type")
        if (data["Modify"]) :
            data["Transfer_Type"] = TRANSFER_T.EDIT_IMAGE
        else :
            data["Transfer_Type"] = TRANSFER_T.CREATE_IMAGE
        data.pop("Modify")
        self.__dbConnector.addToTransferQueue(data)

    def __sendDomainsVNCConnectionData(self):
        '''
        Sends the domains' VNC connection data to the cluster server
        Args:
            None
        Returns:
            Nothing
        '''
        vncConnectionData = self.__dbConnector.getDomainsConnectionData()
        segmentSize = 150
        segmentCounter = 1
        outgoingData = []
        if (len(vncConnectionData) == 0):
            segmentCounter = 0
        segmentNumber = (len(vncConnectionData) / segmentSize)
        if (len(vncConnectionData) % segmentSize != 0) :
            segmentNumber += 1
            sendLastSegment = True
        else :
            sendLastSegment = segmentNumber == 0 
        for connectionParameters in vncConnectionData :
            outgoingData.append(connectionParameters)
            if (len(outgoingData) >= segmentSize) :
                # Flush
                packet = self.__packetManager.createActiveVMsVNCDataPacket(self.__vncServerIP, segmentCounter, segmentNumber, outgoingData)
                self.__networkManager.sendPacket('', self.__listenningPort, packet)
                outgoingData = []
                segmentCounter += 1
        # Send the last segment
        if (sendLastSegment) :
            packet = self.__packetManager.createActiveVMsVNCDataPacket(self.__vncServerIP, segmentCounter, segmentNumber, outgoingData)
            self.__networkManager.sendPacket('', self.__listenningPort, packet)         
    
    def __sendStatusData(self):
        """
        Sends the server's status data to the cluster server
        Args:
            None
        Returns:
            Nothing
        """
        info = self.__domainHandler.getLibvirtStatusInfo()
        realCPUNumber = multiprocessing.cpu_count()
        freeOutput = ChildProcessManager.runCommandInForeground("free -k", VMServerException)
        
        # free's output contains the following lines and collumns:
        #              total       used       free     shared    buffers     cached
        # Mem:    4146708480 3939934208  206774272          0  224706560 1117671424
        # -/+ buffers/cache: 2597556224 1549152256
        # Swap:   2046816256   42455040 2004361216
        #
        # We must get the third line
           
        availableMemory = int(freeOutput.split("\n")[1].split()[1])
        freeMemory = int(freeOutput.split("\n")[2].split()[2])
        
        freeStorageSpace, availableStorageSpace, freeTemporaryStorage, availableTemporaryStorage = self.__generateDiskStats()
        packet = self.__packetManager.createVMServerStatusPacket(self.__vncServerIP, info["#domains"], freeMemory, availableMemory, 
                                                                 freeStorageSpace, availableStorageSpace, 
                                                                 freeTemporaryStorage, availableTemporaryStorage,
                                                                 info["#vcpus"], realCPUNumber)
        self.__networkManager.sendPacket('', self.__listenningPort, packet) 
        
    def __generateDiskStats(self):
        """
        Generates the hard disk usage statistics
        Args:
            None
        Returns:
            the free and available storage and temporary space
        """
        diskStats_storage = os.statvfs(self.__parser.getConfigurationParameter("sourceImagePath"))
        diskStats_temporaryData = os.statvfs(self.__parser.getConfigurationParameter("executionImagePath"))
        allocatedStorageSpace, allocatedTemporaryStorageSpace = self.__checkDiskImagesSpace()
        freeStorageSpace = diskStats_storage.f_bfree * diskStats_storage.f_frsize / 1024 - allocatedStorageSpace
        availableStorageSpace = diskStats_storage.f_bavail * diskStats_storage.f_frsize / 1024
        freeTemporaryStorageSpace = diskStats_temporaryData.f_bfree * diskStats_temporaryData.f_frsize / 1024 - allocatedTemporaryStorageSpace
        availableTemporaryStorageSpace = diskStats_temporaryData.f_bavail * diskStats_temporaryData.f_frsize / 1024
        return freeStorageSpace, availableStorageSpace, freeTemporaryStorageSpace, availableTemporaryStorageSpace
    
    def __checkDiskImagesSpace(self):
        """
        Checks how much disk space must be allocated for the active virtual machines' disk images
        Args:
            None
        Returns:
            the storage and temporary storage space that must be allocated.
        """
        activeDomainNames = self.__dbConnector.getRegisteredDomainNames()
        allocatedStorageSpace = 0
        allocatedTemporaryStorageSpace = 0
        for domainName in activeDomainNames:            
            dataImagePath = self.__dbConnector.getDomainDataImagePath(domainName)
            osImagePath = self.__dbConnector.getDomainOSImagePath(domainName)             
            isEditedImage = self.__dbConnector.getBootableFlag(self.__dbConnector.getDomainImageID(domainName))            
            dataSpace = self.__getAllocatedSpace(dataImagePath)
            if (isEditedImage) :
                osSpace = self.__getAllocatedSpace(osImagePath)
                allocatedStorageSpace += osSpace + dataSpace
            else :
                allocatedTemporaryStorageSpace += dataSpace
                
        return allocatedStorageSpace, allocatedTemporaryStorageSpace
            
    def __getAllocatedSpace(self, imagePath):
        """
        Returns the disk space that must be allocated for a disk image
        Args:
            imagePath: the disk image's path
        Returns:
            Nothing
        """
        try :
            output = ChildProcessManager.runCommandInForeground("qemu-img info " + imagePath, Exception)
            lines = output.split("\n")
            virtualSize = VMServerReactor.__extractImageSize(lines[2].split(":")[1].split("(")[0])
            usedSpace = VMServerReactor.__extractImageSize(lines[3].split(":")[1])            
            return virtualSize - usedSpace
        except Exception as e:
            print e
            return 0
            
    @staticmethod
    def __extractImageSize(string):
        """
        Extracts an image size from a quemu-img command output.
        Args:
            string: the qemu-img command's image size
        Returns:
            the disk image size (in kilobytes)
        """
        if ("G" in string) :
            power = 2
        elif ("M" in string):
            power = 1
        else:
            power = 0                                
        string = string.replace("G", "")
        string = string.replace("M", "")
        string = string.replace("K", "")
        return int(ceil(float(string))) * 1024 ** power        
    
    def __sendActiveDomainUIDs(self):
        """
        Sends domains' UUIDs to the cluster server
        Args:
            None
        Returns:
            Nothing
        """
        activeDomainUIDs = self.__dbConnector.getActiveDomainUIDs()
        packet = self.__packetManager.createActiveDomainUIDsPacket(self.__vncServerIP, activeDomainUIDs)
        self.__networkManager.sendPacket('', self.__listenningPort, packet)
    
    def has_finished(self):
        """
        Checks if the virtual machine server has been shut down or not
        Args:
            None
        Returns:
            Nothing
        """
        return self.__finished   