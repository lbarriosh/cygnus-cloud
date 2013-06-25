# -*- coding: utf8 -*-
'''
    ========================================================================
                                    CygnusCloud
    ========================================================================
    
    File: packetReactor.py    
    Version: 4.0
    Description: cluster endpoint daemon packet reactor
    
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

from clusterServer.packetHandling.packet_t import CLUSTER_SERVER_PACKET_T as PACKET_T
from clusterEndpoint.databases.editionState_t import EDITION_STATE_T
from clusterEndpoint.commands.command_type import COMMAND_TYPE
from clusterEndpoint.commands.command_output_type import COMMAND_OUTPUT_TYPE

class ClusterEndpointPacketReactor(object):  
    """
    These objects process the packets sent from the cluster server
    """    
    def __init__(self, codesTranslator, commandsHandler, packetHandler, commandsProcessor, endpointDBConnector, commandsDBConnector):
        """
        Initializes the packet reactor's state
        Args:
            codesTranslator: the codes translator to use
            commandsHandler. the commands handler to use
            packetHandler: the packet handler to use
            commandsProcessor: the commands processor to use
            endpointDBConnector: the cluster endpoint database connector to use
            commandsDBConnector: the commands database connector to use
        """
        self.__packetHandler = None
        self.__codeTranslator = codesTranslator
        self.__commandsHandler = commandsHandler
        self.__packetHandler = packetHandler
        self.__commandsProcessor = commandsProcessor
        self.__endpointDBConnector = endpointDBConnector
        self.__commandsDBConnector = commandsDBConnector
    
    def processPacket(self, packet):
        """
        Processes a packet sent from the cluster server
        Args:
            packet: the packet to process
        Returns:
            Nothing
        """
        if (self.__commandsProcessor.finish()) :
            return
        data = self.__packetHandler.readPacket(packet)
        if (data["packet_type"] == PACKET_T.VM_SERVERS_STATUS_DATA) :
            self.__processVMServerConfigurationSegment(data)            
        elif (data["packet_type"] == PACKET_T.VM_DISTRIBUTION_DATA) :
            self.__processImageCopiesDistributionSegment(data)            
        elif (data["packet_type"] == PACKET_T.REPOSITORY_STATUS):
            self.__updateImageRepositoryStatus(data)            
        elif (data["packet_type"] == PACKET_T.VM_SERVERS_RESOURCE_USAGE) :
            self.__endpointDBConnector.processVMServerResourceUsageSegment(data["Segment"], data["SequenceSize"], data["Data"])            
        elif (data["packet_type"] == PACKET_T.ACTIVE_VM_VNC_DATA) :
            self.__endpointDBConnector.processActiveVMVNCDataSegment(data["Segment"], data["SequenceSize"], data["VMServerIP"], data["Data"])                        
        else :
            # The remaining packet types contain a command's output
            l = data["CommandID"].split("|")
            commandID = (int(l[0]), float(l[1]))            
            if (data["packet_type"] == PACKET_T.COMMAND_EXECUTED) :
                self.__processCommandExecutedPacket(commandID, data)
            else :           
                if (data["packet_type"] == PACKET_T.VM_CONNECTION_DATA) :
                    self.__processVMConnectionDataPacket(commandID, data)   
                                         
                elif (data["packet_type"] == PACKET_T.IMAGE_CREATED) :                    
                    self.__processImageCreatedPacket(commandID, data)
                else :                    
                    self.__processErrorPacket(commandID, data)
                    
    def __processVMServerConfigurationSegment(self, data):
        """
        Processes a virtual machine server configuration segment
        Args:
            data: the segment's data
        Returns:
            Nothing
        """
        processedData = self.__codeTranslator.processVMServerSegment(data["Data"])
        self.__endpointDBConnector.processVMServerSegment(data["Segment"], data["SequenceSize"], processedData)
        
    def __processImageCopiesDistributionSegment(self, data):
        """
        Processes an image copies distribution segment
        Args:
            data: the segment's data
        Returns:
            Nothing
        """
        processedData = self.__codeTranslator.processImageCopiesDistributionSegment(data["Data"])
        self.__endpointDBConnector.processImageCopiesDistributionSegment(data["Segment"], data["SequenceSize"], processedData)
        
    def __updateImageRepositoryStatus(self, data):
        """
        Processes an image repository status packet
        Args:
            data: the packet to process' data
        Returns:
            Nothing
        """
        status = self.__codeTranslator.translateRepositoryStatusCode(data["RepositoryStatus"])
        self.__endpointDBConnector.updateImageRepositoryStatus(data["FreeDiskSpace"], data["AvailableDiskSpace"], status)
        
    def __processCommandExecutedPacket(self, commandID, data):
        """
        Processes a command executed packet, generating notifications when necessary
        Args:
            commandID: the executed command's ID
            data: the received packet's data
        Returns:
            Nothing
        """
        commandData = self.__commandsDBConnector.removeExecutedCommand(commandID)
        output_type = None                       
        if (commandData["CommandType"] == COMMAND_TYPE.EDIT_IMAGE or commandData["CommandType"] == COMMAND_TYPE.CREATE_IMAGE) :
            # Una imagen se ha acabado de editar
            self.__endpointDBConnector.updateEditedImageState(data["CommandID"], EDITION_STATE_T.CHANGES_NOT_APPLIED)                    
            if (commandData["CommandType"] == COMMAND_TYPE.EDIT_IMAGE) :
                output_type = COMMAND_OUTPUT_TYPE.IMAGE_EDITED                        
            else :
                output_type == COMMAND_OUTPUT_TYPE.IMAGE_CREATED
                        
        elif (commandData["CommandType"] == COMMAND_TYPE.DEPLOY_IMAGE or commandData["CommandType"] == COMMAND_TYPE.AUTO_DEPLOY_IMAGE) :                    
            if (self.__endpointDBConnector.affectsToNewOrEditedImage(data["CommandID"])) :
                # Mover la fila
                self.__endpointDBConnector.moveRowToImage(data["CommandID"])                        
            else:
                parsedArgs = self.__commandsHandler.deserializeCommandArgs(commandData["CommandType"], commandData["CommandArgs"])
                self.__endpointDBConnector.makeBootable(parsedArgs["ImageID"])                        
            output_type = COMMAND_OUTPUT_TYPE.IMAGE_DEPLOYED
                    
        elif (commandData["CommandType"] == COMMAND_TYPE.DELETE_IMAGE or commandData["CommandType"] == COMMAND_TYPE.DELETE_IMAGE_FROM_INFRASTRUCTURE) :
            output_type = COMMAND_OUTPUT_TYPE.IMAGE_DELETED
                                
        if (output_type != None) :
                self.__commandsDBConnector.addCommandOutput(commandID, output_type, 
                                                                self.__codeTranslator.translateNotificationCode(commandData["CommandType"]), 
                                                                True)
                
    def __processVMConnectionDataPacket(self, commandID, data):
        """
        Processes a virtual machine connection data packet
        Args:
            commandID: a command ID
            data: the incoming packet's data
        Returns:
            Nothing
        """
        commandData = self.__commandsDBConnector.getCommandData(commandID)                    
        if (commandData["CommandType"] == COMMAND_TYPE.VM_BOOT_REQUEST) :
            (outputType, outputContent) = self.__commandsHandler.createVMConnectionDataOutput(
                data["VNCServerIPAddress"], data["VNCServerPort"], data["VNCServerPassword"]) 
            self.__commandsDBConnector.addCommandOutput(commandID, outputType, outputContent)                        
        else :
            self.__endpointDBConnector.updateEditedImageState(data["CommandID"], EDITION_STATE_T.VM_ON)
                
    def __processImageCreatedPacket(self, commandID, data):
        """
        Processes an image created packet
        Args:
            commandID: a command ID
            data: the incoming packet's data
        Returns:
            Nothing
        """
        self.__endpointDBConnector.registerImageID(data["CommandID"], data["ImageID"])
        self.__commandsDBConnector.addCommandOutput(commandID, COMMAND_OUTPUT_TYPE.IMAGE_CREATED,
                self.__codeTranslator.translateNotificationCode(COMMAND_TYPE.CREATE_IMAGE),
                True)
        
    def __processErrorPacket(self, commandID, data):
        """
        Processes an error packet
        Args:
            commandID: a command ID
            data: the incoming packet's data
        Returns:
            Nothing
        """        
        if (data["packet_type"] == PACKET_T.IMAGE_CREATION_ERROR) :
            self.__endpointDBConnector.deleteEditedImage(data["CommandID"])
                        
        elif (data["packet_type"] == PACKET_T.IMAGE_EDITION_ERROR):
            self.__endpointDBConnector.updateEditedImageState(data["CommandID"], EDITION_STATE_T.CHANGES_NOT_APPLIED, None)     
                        
        elif (data["packet_type"] == PACKET_T.AUTO_DEPLOY_ERROR):
            if (self.__endpointDBConnector.affectsToNewOrEditedImage(data["CommandID"])) :                            
                self.__endpointDBConnector.updateEditedImageState(data["CommandID"], EDITION_STATE_T.AUTO_DEPLOYMENT_ERROR)    
                    
        isNotification = data["packet_type"] == PACKET_T.IMAGE_DEPLOYMENT_ERROR or\
            data["packet_type"] == PACKET_T.DELETE_IMAGE_FROM_SERVER_ERROR or\
            data["packet_type"] == PACKET_T.DELETE_IMAGE_FROM_INFRASTRUCTURE_ERROR or\
            data["packet_type"] == PACKET_T.AUTO_DEPLOY_ERROR or\
            data["packet_type"] == PACKET_T.IMAGE_CREATION_ERROR or\
            data["packet_type"] == PACKET_T.IMAGE_EDITION_ERROR                            
                                          
        (outputType, outputContent) = self.__commandsHandler.createErrorOutput(data['packet_type'], 
            data["ErrorDescription"])
                
        self.__commandsDBConnector.addCommandOutput(commandID, outputType, outputContent, isNotification)