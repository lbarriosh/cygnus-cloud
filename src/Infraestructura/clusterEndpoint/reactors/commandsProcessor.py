# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: commandsProcessor.py    
    Version: 4.0
    Description: cluster endpoint daemon commands processor
    
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

from time import sleep
from clusterEndpoint.commands.command_type import COMMAND_TYPE
from clusterServer.packetHandling.packet_t import CLUSTER_SERVER_PACKET_T as PACKET_T
from clusterEndpoint.databases.editionState_t import EDITION_STATE_T

class CommandsProcessor(object):
    """
    These objects process the users' requests
    """
    
    def __init__(self, commandsHandler, clusterServerPacketHandler, networkManager, 
                 clusterServerIP, clusterServerPort, commandsDBConnector, endpointDBConnector):
        """
        Initializes the commands processor's state
        Args:
            commandsHandler: the commands handler object to use
            clusterServerPacketHandler: the cluster server packet handler object to use
            networkManager: the NetworkManager object to use
            clusterServerIP: the cluster server's IP address
            clusterServerPort: the cluster server's port
            commandsDBConnector: the commands database connector
            endpointDBConnector: the cluster endpoint database connector
        """
        self.__stopped = False
        self.__commandsHandler = commandsHandler
        self.__commandsDBConnector = commandsDBConnector
        self.__packetHandler = clusterServerPacketHandler
        self.__endpointDBConnector = endpointDBConnector
        self.__networkManager = networkManager
        self.__clusterServerIP = clusterServerIP
        self.__clusterServerPort = clusterServerPort
        self.__haltVMServers = False
                
    def finish(self):
        """
        Checks if a HALT command has been received or not
        Args:
            None
        Returns:
            True if a HALT command was received, and false if it wasn't.
        """
        return self.__stopped
    
    def haltVMServers(self):
        """
        Checks if all the virtual machines should be immediately destroyed or not
        Args:
            None
        Returns:
            True if all the virtual machines must be immediately destroyed, and False otherwise.
        """
        return self.__haltVMServers
        
    def processCommands(self):
        """
        Processes the users' requests
        Args:
            None
        Returns:
            Nothing
        """
        while not self.__stopped :
            commandData = self.__commandsDBConnector.popCommand()
            if (commandData == None) :
                sleep(0.1)
            else :
                (commandID, commandType, commandArgs) = commandData
                parsedArgs = self.__commandsHandler.deserializeCommandArgs(commandType, commandArgs)
                if (commandType != COMMAND_TYPE.HALT) :
                    serializedCommandID = "{0}|{1}".format(commandID[0], commandID[1])                    
                    if (commandType == COMMAND_TYPE.BOOTUP_VM_SERVER) :                    
                        packet = self.__packetHandler.createVMServerBootPacket(parsedArgs["VMServerNameOrIP"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.REGISTER_VM_SERVER) :
                        packet = self.__packetHandler.createVMServerRegistrationPacket(parsedArgs["VMServerIP"], 
                            parsedArgs["VMServerPort"], parsedArgs["VMServerName"], parsedArgs["IsVanillaServer"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.UNREGISTER_OR_SHUTDOWN_VM_SERVER) :
                        packet = self.__packetHandler.createVMServerUnregistrationOrShutdownPacket(parsedArgs["VMServerNameOrIP"], 
                            parsedArgs["Halt"], parsedArgs["Unregister"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.VM_BOOT_REQUEST) :
                        packet = self.__packetHandler.createVMBootRequestPacket(parsedArgs["VMID"], parsedArgs["UserID"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.DESTROY_DOMAIN):
                        packet = self.__packetHandler.createDomainDestructionPacket(parsedArgs["DomainID"], serializedCommandID)
                        self.__endpointDBConnector.unregisterDomain(parsedArgs["DomainID"])
                    elif (commandType == COMMAND_TYPE.REBOOT_DOMAIN):
                        packet = self.__packetHandler.createDomainRebootPacket(parsedArgs["DomainID"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.VM_SERVER_CONFIGURATION_CHANGE) :
                        packet = self.__packetHandler.createVMServerConfigurationChangePacket(parsedArgs["VMServerNameOrIPAddress"],  parsedArgs["NewServerName"],
                                                                                         parsedArgs["NewServerIPAddress"], parsedArgs["NewServerPort"],
                                                                                         parsedArgs["NewVanillaImageEditionBehavior"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.DEPLOY_IMAGE):
                        packet = self.__packetHandler.createImageDeploymentPacket(PACKET_T.DEPLOY_IMAGE, parsedArgs["VMServerNameOrIPAddress"], 
                                                                                     parsedArgs["ImageID"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.DELETE_IMAGE):
                        packet = self.__packetHandler.createImageDeploymentPacket(PACKET_T.DELETE_IMAGE_FROM_SERVER, parsedArgs["VMServerNameOrIPAddress"], 
                                                                                     parsedArgs["ImageID"], serializedCommandID)     
                    elif (commandType == COMMAND_TYPE.CREATE_IMAGE):
                        self.__endpointDBConnector.addNewImage(serializedCommandID, parsedArgs["BaseImageID"], parsedArgs["OwnerID"], 
                                                               parsedArgs["ImageName"], parsedArgs["ImageDescription"])
                        packet = self.__packetHandler.createImageEditionPacket(PACKET_T.CREATE_IMAGE, parsedArgs["BaseImageID"], 
                                                                                  parsedArgs["OwnerID"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.EDIT_IMAGE):   
                        self.__endpointDBConnector.editImage(serializedCommandID, parsedArgs["ImageID"], parsedArgs["OwnerID"])
                        packet = self.__packetHandler.createImageEditionPacket(PACKET_T.EDIT_IMAGE, parsedArgs["ImageID"], parsedArgs["OwnerID"], serializedCommandID)  
                   
                    elif (commandType == COMMAND_TYPE.DELETE_IMAGE_FROM_INFRASTRUCTURE):
                        self.__endpointDBConnector.deleteImage(parsedArgs["ImageID"])
                        packet = self.__packetHandler.createFullImageDeletionPacket(parsedArgs["ImageID"], serializedCommandID)
                    
                    elif (commandType == COMMAND_TYPE.AUTO_DEPLOY_IMAGE):
                        if (self.__endpointDBConnector.affectsToNewOrEditedImage(serializedCommandID)) :
                            self.__endpointDBConnector.updateEditedImageState(serializedCommandID, EDITION_STATE_T.AUTO_DEPLOYMENT)
                        packet = self.__packetHandler.createAutoDeployPacket(parsedArgs["ImageID"], parsedArgs["MaxInstances"], serializedCommandID)
                                          
                    errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, packet)
                    if (errorMessage != None) :
                        (outputType, outputContent) = self.__commandsHandler.createConnectionErrorOutput()
                        self.__commandsDBConnector.addCommandOutput(commandID, outputType, outputContent)
                        
                else :
                    self.__stopped = True
                    self.__haltVMServers = parsedArgs["HaltVMServers"]