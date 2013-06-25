# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: compressionThread.py    
    Version: 3.0
    Description: compression thread definitions
    
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

from ccutils.threads.basicThread import BasicThread
from ccutils.compression.zipBasedCompressor import ZipBasedCompressor
from virtualMachineServer.exceptions.vmServerException import VMServerException
from os import path, listdir, makedirs
import shutil
from ccutils.processes.childProcessManager import ChildProcessManager
from virtualMachineServer.database.transfer_t import TRANSFER_T
from virtualMachineServer.packetHandling.packet_t import VM_SERVER_PACKET_T
from errors.codes import ERROR_DESC_T
from time import sleep

class CompressionThread(BasicThread):
    """
    This thread class is associated with the compression thread
    """
    
    def __init__(self, transferDirectory, diskImagesDirectory, definitionFileDirectory, dbConnector, domainHandler,
                 networkManager, serverListenningPort, packetHandler):
        """
        Initializes the compression thread's state
        Args:
            transferDirectory: the transfers directory
            diskImagesDirectory: the directory where the disk images are stored
            definitionFileDirectory: the directory where the definition files are stored
            dbConnector: the database connector
            domainHandler: the domain handler to use
            networkManger: the network manager to use
            serverListenningPort: the virtual machine server's control connection port.
            packetHandler: the packet handler to use
        """
        BasicThread.__init__(self, "File compression thread")
        self.__diskImagesDirectory = diskImagesDirectory
        self.__transferDirectory = transferDirectory
        self.__definitionFileDirectory = definitionFileDirectory
        self.__dbConnector = dbConnector
        self.__domainHandler = domainHandler
        self.__compressor = ZipBasedCompressor()
        self.__networkManager = networkManager
        self.__serverListenningPort = serverListenningPort
        self.__packetHandler = packetHandler
        
    def run(self):
        while not self.finish() :
            data = self.__dbConnector.peekFromCompressionQueue()
            if (data == None):
                sleep(0.5)
            else:
                self.__processElement(data)
                self.__dbConnector.removeFirstElementFromCompressionQueue()

        
    def __processElement(self, data):
        """
        Processes a compression/decompression requiest
        Args:
            data: a dictionary containing the request's data
        Returns:
            Nothing
        """        
        try :
            imageDirectory = None
            definitionFileDirectory = None
            zipFilePath = None
            if(data["Transfer_Type"] != TRANSFER_T.STORE_IMAGE):                   
                
                self.__dbConnector.deleteImage(data["SourceImageID"])
                    
                # Extract the .zip file
                imageDirectory = path.join(self.__diskImagesDirectory, str(data["TargetImageID"]))
                # Change the extracted files' permissions, and look for the definition file.
                definitionFileDirectory = path.join(self.__definitionFileDirectory, str(data["TargetImageID"]))            
                
                try :
                    ChildProcessManager.runCommandInForeground("rm -rf " + imageDirectory, Exception)
                    ChildProcessManager.runCommandInForeground("rm -rf " + definitionFileDirectory, Exception)
                except Exception:
                    pass
                zipFilePath = path.join(self.__transferDirectory, str(data["SourceImageID"]) + ".zip")
                self.__compressor.extractFile(zipFilePath, imageDirectory)                     
                
                # Move the three extracted files
                if not path.exists(definitionFileDirectory):
                    makedirs(definitionFileDirectory)
            
                definitionFileFound = False
                containsDataFile = False
                containsOSFile = False
                for fileName in listdir(imageDirectory):
                    ChildProcessManager.runCommandInForegroundAsRoot("chmod 666 " + path.join(imageDirectory, fileName), VMServerException)
                    if fileName.endswith(".xml"):
                        definitionFile = fileName
                        shutil.move(path.join(imageDirectory, fileName), definitionFileDirectory)
                        definitionFileFound = True
                    containsDataFile = fileName == "Data.qcow2" or containsDataFile
                    containsOSFile = fileName == "OS.qcow2" or containsOSFile 
                if(not definitionFileFound):
                    raise Exception("The definition file was not found")
                if (not containsDataFile) :
                    raise Exception("The data disk image was not found")
                if (not containsOSFile) :
                    raise Exception("The OS disk image was not found")
    
                # Register the new image
                self.__dbConnector.createImage(data["TargetImageID"], path.join(str(data["TargetImageID"]), "OS.qcow2"),
                                               path.join(str(data["TargetImageID"]), "Data.qcow2"),
                                               path.join(str(data["TargetImageID"]), definitionFile), data["Transfer_Type"] == TRANSFER_T.DEPLOY_IMAGE)
                
                if (data["Transfer_Type"] != TRANSFER_T.DEPLOY_IMAGE):                
                    # Edition request => boot the virtual machine, store the image repository connection data
                    self.__dbConnector.addValueToConnectionDataDictionary(data["CommandID"], {"RepositoryIP": data["RepositoryIP"], "RepositoryPort" : data["RepositoryPort"]})                
                    
                    self.__domainHandler.createDomain(data["TargetImageID"], data["UserID"], data["CommandID"])        
                else :
                    p = self.__packetHandler.createConfirmationPacket(VM_SERVER_PACKET_T.IMAGE_DEPLOYED, data["TargetImageID"], data["CommandID"])
                    self.__networkManager.sendPacket('', self.__serverListenningPort, p)
                    
                # Delete the .zip file
                ChildProcessManager.runCommandInForeground("rm " + zipFilePath, VMServerException)    
            else:        
                # Build the .zip file
                
                zipFilePath = path.join(self.__transferDirectory, str(data["TargetImageID"]) + ".zip")                
                
                self.__compressor.createCompressedFile(zipFilePath, [data["OSImagePath"], 
                    data["DataImagePath"], path.join(self.__definitionFileDirectory, data["DefinitionFilePath"])])
                
                
                # Delete the source files
                ChildProcessManager.runCommandInForeground("rm -rf " + path.dirname(path.join(self.__definitionFileDirectory, data["DefinitionFilePath"])), Exception)
                ChildProcessManager.runCommandInForeground("rm -rf " + path.dirname(data["OSImagePath"]), Exception)
                
                # Queue a transfer request
                
                data.pop("DataImagePath")
                data.pop("OSImagePath")
                data.pop("DefinitionFilePath")
               
                data["SourceFilePath"] = path.basename(zipFilePath)        
                
                self.__dbConnector.addToTransferQueue(data)
        except Exception:
            if (data["Transfer_Type"] == TRANSFER_T.DEPLOY_IMAGE):
                packet_type = VM_SERVER_PACKET_T.IMAGE_DEPLOYMENT_ERROR
            else :
                packet_type = VM_SERVER_PACKET_T.IMAGE_EDITION_ERROR
                
            p = self.__packetHandler.createErrorPacket(packet_type, ERROR_DESC_T.VMSRVR_COMPRESSION_ERROR, data["CommandID"])
            self.__networkManager.sendPacket('', self.__serverListenningPort, p)
            if (data["Transfer_Type"] != TRANSFER_T.DEPLOY_IMAGE):
                # Build a special transfer to unlock the disk image
                transfer = dict()
                transfer["Transfer_Type"] = TRANSFER_T.CANCEL_EDITION
                transfer["RepositoryIP"] = data["RepositoryIP"]
                transfer["RepositoryPort"] = data["RepositoryPort"]
                transfer["CommandID"] = data["CommandID"]
                transfer["ImageID"] = data["TargetImageID"]
                self.__dbConnector.addToTransferQueue(transfer)
            
            # Delete the disk images, the definition file and the .zip file.
            if (imageDirectory != None):
                ChildProcessManager.runCommandInForeground("rm -rf " + imageDirectory, None)
            if (definitionFileDirectory != None):
                ChildProcessManager.runCommandInForeground("rm -rf " + definitionFileDirectory, None)
            if (zipFilePath != None):
                ChildProcessManager.runCommandInForeground("rm -rf " + zipFilePath, None)