'''
Created on Jun 2, 2013

@author: luis
'''

from time import sleep
from clusterEndpoint.commands.command_type import COMMAND_TYPE
from clusterServer.packetHandling.packet_t import CLUSTER_SERVER_PACKET_T as PACKET_T
from clusterEndpoint.databases.editionState_t import EDITION_STATE_T

class CommandsProcessor(object):
    
    def __init__(self, commandsHandler, webPacketHandler, networkManager, 
                 clusterServerIP, clusterServerPort, commandsDBConnector, endpointDBConnector):
        self.__stopped = False
        self.__commandsHandler = commandsHandler
        self.__commandsDBConnector = commandsDBConnector
        self.__packetHandler = webPacketHandler
        self.__endpointDBConnector = endpointDBConnector
        self.__networkManager = networkManager
        self.__clusterServerIP = clusterServerIP
        self.__clusterServerPort = clusterServerPort
        self.__haltVMServers = False
                
    def finish(self):
        return self.__stopped
    
    def haltVMServers(self):
        return self.__haltVMServers
        
    def processCommands(self):
        """
        Procesa los comandos enviados desde los conectores
        Argumentos:
            Ninguno
        Devuelve:
            Nada
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
                        packet = self.__packetHandler.createVMServerBootUpPacket(parsedArgs["VMServerNameOrIP"], serializedCommandID)
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
                        self.__endpointDBConnector.unregisterDomain(parsedArgs["DomainUID"])
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
                        # Añadir la imagen a la base de datos
                        self.__endpointDBConnector.addNewImage(serializedCommandID, parsedArgs["BaseImageID"], parsedArgs["OwnerID"], 
                                                               parsedArgs["ImageName"], parsedArgs["ImageDescription"])
                        packet = self.__packetHandler.createImageEditionPacket(PACKET_T.CREATE_IMAGE, parsedArgs["BaseImageID"], 
                                                                                  parsedArgs["OwnerID"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.EDIT_IMAGE):   
                        # Actualizar los flags de la imagen en la base de datos
                        self.__endpointDBConnector.editImage(serializedCommandID, parsedArgs["ImageID"], parsedArgs["OwnerID"])
                        packet = self.__packetHandler.createImageEditionPacket(PACKET_T.EDIT_IMAGE, parsedArgs["ImageID"], parsedArgs["OwnerID"], serializedCommandID)  
                    elif (commandType == COMMAND_TYPE.DELETE_IMAGE_FROM_INFRASTRUCTURE):
                        packet = self.__packetHandler.createImageDeletionPacket(parsedArgs["ImageID"], serializedCommandID)
                    elif (commandType == COMMAND_TYPE.AUTO_DEPLOY_IMAGE):
                        if (self.__endpointDBConnector.affectsToNewOrEditedImage(serializedCommandID)) :
                            self.__endpointDBConnector.updateEditedImageStatus(serializedCommandID, EDITION_STATE_T.AUTO_DEPLOYMENT)
                        packet = self.__packetHandler.createAutoDeployPacket(parsedArgs["ImageID"], parsedArgs["MaxInstances"], serializedCommandID)
                                          
                    errorMessage = self.__networkManager.sendPacket(self.__clusterServerIP, self.__clusterServerPort, packet)
                    if (errorMessage != None) :
                        # Error al enviar el paquete => el comando no se podrá ejecutar => avisar a la web
                        (outputType, outputContent) = self.__commandsHandler.createConnectionErrorOutput()
                        self.__commandsDBConnector.addCommandOutput(commandID, outputType, outputContent)
                        
                else :
                    self.__stopped = True
                    self.__haltVMServers = parsedArgs["HaltVMServers"]