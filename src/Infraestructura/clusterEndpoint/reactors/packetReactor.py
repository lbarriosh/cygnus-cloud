# -*- coding: utf8 -*-
'''
Definiciones del endpoint de la web
@author: Luis Barrios Hernández
@version: 3.5
'''

from clusterServer.packetHandling.packet_t import CLUSTER_SERVER_PACKET_T as PACKET_T
from clusterEndpoint.databases.editionState_t import EDITION_STATE_T
from clusterEndpoint.commands.command_type import COMMAND_TYPE
from clusterEndpoint.commands.command_output_type import COMMAND_OUTPUT_TYPE

class ClusterEndpointPacketReactor(object):  
    """
    Estos objetos comunican un servidor de cluster con la web
    """    
    def __init__(self, codeTranslator, commandsHandler, packetHandler, commandsProcessor, endpointDBConnector, commandsDBConnector):
        """
        Inicializa el estado del endpoint
        Argumentos:
            Ninguno
        """
        self.__packetHandler = None
        self.__codeTranslator = codeTranslator
        self.__commandsHandler = commandsHandler
        self.__packetHandler = packetHandler
        self.__commandsProcessor = commandsProcessor
        self.__endpointDBConnector = endpointDBConnector
        self.__commandsDBConnector = commandsDBConnector
    
    def processPacket(self, packet):
        """
        Procesa un paquete enviado desde el servidor de cluster
        Argumentos:
            packet: el paquete a procesar
        Devuelve:
            Nada
        """
        if (self.__commandsProcessor.finish()) :
            return
        data = self.__packetHandler.readPacket(packet)
        if (data["packet_type"] == PACKET_T.VM_SERVERS_STATUS_DATA) :
            self.__processVMServerSegment(data)            
        elif (data["packet_type"] == PACKET_T.VM_DISTRIBUTION_DATA) :
            self.__processImageCopiesDistributionSegment(data)            
        elif (data["packet_type"] == PACKET_T.REPOSITORY_STATUS):
            self.__updateImageRepositoryStatus(data)            
        elif (data["packet_type"] == PACKET_T.VM_SERVERS_RESOURCE_USAGE) :
            self.__endpointDBConnector.processVMServerResourceUsageSegment(data["Segment"], data["SequenceSize"], data["Data"])            
        elif (data["packet_type"] == PACKET_T.ACTIVE_VM_VNC_DATA) :
            self.__endpointDBConnector.processActiveVMVNCDataSegment(data["Segment"], data["SequenceSize"], data["VMServerIP"], data["Data"])                        
        else :
            # El resto de paquetes contienen la salida de un comando
            l = data["CommandID"].split("|")
            commandID = (int(l[0]), float(l[1]))            
            if (data["packet_type"] == PACKET_T.COMMAND_EXECUTED) :
                self.__processCommandExecutedPacket(commandID, data)
            else :           
                # El resto de paquetes contienen el resultado de ejecutar comandos => los serializamos y los añadimos
                # a la base de datos de comandos para que los conectores se enteren        
                if (data["packet_type"] == PACKET_T.VM_CONNECTION_DATA) :
                    self.__processVMConnectionDataPacket(commandID, data)   
                                         
                elif (data["packet_type"] == PACKET_T.IMAGE_CREATED) :                    
                    self.__processImageCreatedPacket(commandID, data)
                else :                    
                    self.__processErrorPacket(commandID, data)
                    
    def __processVMServerSegment(self, data):
        processedData = self.__codeTranslator.processVMServerSegment(data["Data"])
        self.__endpointDBConnector.processVMServerSegment(data["Segment"], data["SequenceSize"], processedData)
        
    def __processImageCopiesDistributionSegment(self, data):
        processedData = self.__codeTranslator.processImageCopiesDistributionSegment(data["Data"])
        self.__endpointDBConnector.processImageCopiesDistributionSegment(data["Segment"], data["SequenceSize"], processedData)
        
    def __updateImageRepositoryStatus(self, data):
        status = self.__codeTranslator.translateRepositoryStatusCode(data["RepositoryStatus"])
        self.__endpointDBConnector.updateImageRepositoryStatus(data["FreeDiskSpace"], data["AvailableDiskSpace"], status)
        
    def __processCommandExecutedPacket(self, commandID, data):
        # Comandos ejecutados => generar notificaciones cuando sea necesario
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
        # Generar salida sólo si se trata de un comando de arranque de una máquina virtual
            commandData = self.__commandsDBConnector.getCommandData(commandID)                    
            if (commandData["CommandType"] == COMMAND_TYPE.VM_BOOT_REQUEST) :
                (outputType, outputContent) = self.__commandsHandler.createVMConnectionDataOutput(
                            data["VNCServerIPAddress"], data["VNCServerPort"], data["VNCServerPassword"]) 
                self.__commandsDBConnector.addCommandOutput(commandID, outputType, outputContent)                        
            else :
                # Cambiar el estado de la imagen en edición
                self.__endpointDBConnector.updateEditedImageState(data["CommandID"], EDITION_STATE_T.VM_ON)
                
    def __processImageCreatedPacket(self, commandID, data):
        self.__endpointDBConnector.registerImageID(data["CommandID"], data["ImageID"])
        self.__commandsDBConnector.addCommandOutput(commandID, COMMAND_OUTPUT_TYPE.IMAGE_CREATED,
                self.__codeTranslator.translateNotificationCode(COMMAND_TYPE.CREATE_IMAGE),
                True)
        
    def __processErrorPacket(self, commandID, data):
        # Errores
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