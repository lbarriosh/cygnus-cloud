# -*- coding: utf8 -*-
'''
Conector que usará la web para interactuar con el sistema
@author: Luis Barrios Hernández
@version: 4.0
'''
from clusterEndpoint.databases.clusterEndpointDB import ClusterEndpointDBConnector
from clusterEndpoint.databases.commandsDatabaseConnector import CommandsDatabaseConnector
from clusterEndpoint.commands.commandsHandler import CommandsHandler
from clusterEndpoint.codes.spanishCodesTranslator import SpanishCodesTranslator
from time import sleep

class ClusterConnector(object):
    """
    Estos objetos comunican la web y el endpoint a través de memoria compartida.
    """
    
    def __init__(self, userID):
        """
        Inicializa el estado del conector
        Argumentos:
            userID: el identificador del usuario que accede al sistema. Se trata de un entero.
        """
        self.__userID = userID
        self.__commandsHandler = CommandsHandler(SpanishCodesTranslator())
    
    def connectToDatabases(self, endpointDBName, commandsDBName, databaseUser, databasePassword):
        """
        Establece una conexión con las bases de datos de estado y comandos.
        Argumentos:
            endpointDBName: el nombre de la base de datos de estado
            commandsDBName: el nombre de la base de datos de comandos
            databaseUser: el nombre de usuario con el que se accederá a las dos bases de datos
            databasePassword: la contraseña para acceder a las bases de datos
        Devuelve:
            Nada
        """
        self.__endpointDBConnector = ClusterEndpointDBConnector(databaseUser, databasePassword, endpointDBName)
        self.__commandsDBConnector = CommandsDatabaseConnector(databaseUser, databasePassword, commandsDBName, 1)
        
    def dispose(self):
        """
        Cierra las conexiones con las bases de datos
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        pass
        
    def getActiveVMsData(self, showAllVMs=False):
        """
        Devuelve los datos de las máquinas virtuales activas
        Argumentos:
            showAllVMs: si es True, se muestran los datos de todas las máquinas activas; si es False, sólo
            las del usuario registrado en el conector
        Devuelve: una lista de diccionarios con los datos de las máquinas virtuales activas
        """
        if not showAllVMs :
            userID = self.__userID
        else :
            userID = None
        return self.__endpointDBConnector.getActiveVMsData(userID)
    
    def getVMDistributionData(self):
        """
        Devuelve los datos de distribución de las imágenes
        Argumentos:
            Ninguno
        Devuelve: una lista de diccionarios con los datos de distribución de las imágenes
        """
        return self.__endpointDBConnector.getVMDistributionData()
        
    def getVMServersData(self):
        """
        Devuelve los datos básicos de los servidores de máquinas virtuales
        Argumentos:
            Ninguno
        Devuelve: una lista de diccionarios con los datos básicos de los servidores de máquinas virtuales
        """
        return self.__endpointDBConnector.getVMServersData()
        
    def registerVMServer(self, vmServerIP, vmServerPort, vmServerName, isVanillaServer):
        """
        Registra un servidor de máquinas virtuales
        Argumentos:
            vmServerIP: la IP del servidor de máquinas virtuales
            vmServerPort: el puerto en el que escucha
            vmServerName: el nombre del servidor de máquinas virtuales
            isVanillaServer: indica si el servidor de máquinas virtuales se usará preferentemente
                para editar imágenes vanilla o no.
        Devuelve:
            El identificador único del comando.
            @attention: La representación del identificador único del comando puede cambiar sin previo aviso.
        """
        (commandType, commandArgs) = self.__commandsHandler.createVMServerRegistrationCommand(vmServerIP, vmServerPort, vmServerName, isVanillaServer)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
        
    def unregisterVMServer(self, vmServerNameOrIP, isShutDown):
        """
        Borra un servidor de máquinas virtuales
        Argumentos:
            vmServerNameOrIP: el nombre o la IP del servidor a borrar
            isShutDown: si es True, el servidor se apagará inmediatamente. Si es False, esperará a que los usuarios apaguen sus
            máquinas virtuales.
        Devuelve:
            El identificador único del comando.
            @attention: La representación del identificador único del comando puede cambiar sin previo aviso.
        """
        (commandType, commandArgs) = self.__commandsHandler.createVMServerUnregistrationOrShutdownCommand(True, vmServerNameOrIP, isShutDown)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def shutdownVMServer(self, vmServerNameOrIP, isShutDown):
        """
        Apaga un servidor de máquinas virtuales
        Argumentos:
            vmServerNameOrIP: el nombre o la IP del servidor a borrar
            isShutDown: si es True, el servidor se apagará inmediatamente. Si es False, esperará a que los usuarios apaguen sus
            máquinas virtuales.
        Devuelve:
            El identificador único del comando.
            @attention: La representación del identificador único del comando puede cambiar sin previo aviso.
        """
        (commandType, commandArgs) = self.__commandsHandler.createVMServerUnregistrationOrShutdownCommand(False, vmServerNameOrIP, isShutDown)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def bootUpVMServer(self, vmServerNameOrIP):
        """
        Arranca un servidor de máquinas virtuales y lo añade a la infraestructura
        Argumentos:
            vmServerNameOrIP: el nombre o la IP del servidor a arrancar
        Devuelve:
            El identificador único del comando.
            @attention: La representación del identificador único del comando puede cambiar sin previo aviso.
        """
        (commandType, commandArgs) = self.__commandsHandler.createVMServerBootCommand(vmServerNameOrIP)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def bootUpVM(self, imageID):
        """
        Solicita a la infraestructura el arranque de una máquina virtual
        Argumentos:
            imageID: el identificador único de la imagen a arrancar
        Devuelve:
            El identificador único del comando.
            @attention: La representación del identificador único del comando puede cambiar sin previo aviso.
        """
        (commandType, commandArgs) = self.__commandsHandler.createVMBootCommand(imageID, self.__userID)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def isShutDown(self, haltVMServers):
        """
        Apaga toda la infraestructura
        Argumentos:
            haltVMServers: si es True, el servidor se apagará inmediatamente. Si es False, esperará a que los usuarios apaguen sus
            máquinas virtuales.
        Devuelve: 
            Nada
        """
        (commandType, commandArgs) = self.__commandsHandler.createHaltCommand(haltVMServers)
        self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
        
    def destroyDomain(self, domainID):
        """
        Destruye una máquina virtual
        Argumentos:
            domainID: el identificador único de la máquina virtual a destruir
        Devuelve:
            Nada
        """
        (commandType, commandArgs) = self.__commandsHandler.createDomainDestructionCommand(domainID)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def deployImage(self, serverNameOrIPAddress, imageID):
        (commandType, commandArgs) = self.__commandsHandler.createImageDeploymentCommand(True, serverNameOrIPAddress, imageID)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def deleteImage(self, serverNameOrIPAddress, imageID):
        (commandType, commandArgs) = self.__commandsHandler.createImageDeploymentCommand(False, serverNameOrIPAddress, imageID)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def createImage(self, baseImageID, imageName, imageDescription, imageID):
        (commandType, commandArgs) = self.__commandsHandler.createImageAdditionCommand(self.__userID, baseImageID, imageName, imageDescription)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def editImage(self, imageID):
        (commandType, commandArgs) = self.__commandsHandler.createImageEditionCommand(imageID, self.__userID)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def deleteImageFromInfrastructure(self, imageID):
        (commandType, commandArgs) = self.__commandsHandler.createDeleteImageFromInfrastructureCommand(imageID)        
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def deployEditedImage(self, imageID):
        (commandType, commandArgs) = self.__commandsHandler.createAutoDeploymentCommand(imageID, -1)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def autoDeployImage(self, imageID, max_instances):
        (commandType, commandArgs) = self.__commandsHandler.createAutoDeploymentCommand(imageID, max_instances)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def changeVMServerConfiguration(self, serverNameOrIPAddress, newName, newIPAddress, newPort, 
                                    newVanillaImageEditionBehavior):
        (commandType, commandArgs) = self.__commandsHandler.createVMServerConfigurationChangeCommand(serverNameOrIPAddress, 
            newName, newIPAddress, newPort, newVanillaImageEditionBehavior)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def getCommandOutput(self, commandID):
        """
        Devuelve la salida de un comando
        Argumentos:
            commandID: el identificador único del comando
        Devuelve:
            - Si el comando todavía se está ejecutando, se devuelve una tupla vacía.
            - Si el comando se ha terminado de ejecutar, se devuelve un diccionario
              con los datos de su salida.
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
        Espera a que un comando termine, devolviendo su salida en caso de que la haya.
        Argumentos:
            commandID: el identificador único del comando
        Devuelve: 
            - None si el comando no tiene salida
            - Un diccionario con los datos de su salida en caso contrario
        @attention: Este método es bloqueante. Si se desea un comportamiento no bloqueante,
        es necesario utilizar el método getCommandOutput.
        """
        while (self.__commandsDBConnector.isRunning(commandID)) :
                sleep(0.1)
        result = self.__commandsDBConnector.getCommandOutput(commandID)
        if result == None :
            return None
        else :
            return self.__commandsHandler.deserializeCommandOutput(result[0], result[1])
        
    def getImageBasicData(self, imageID):
        """
        Devuelve los datos de una imagen
        """
        return self.__endpointDBConnector.getImageBasicData(imageID)
        
    def getBootableImagesData(self, imageIDs):
        """
        Devuelve los datos de las imágenes arrancables
        """
        return self.__endpointDBConnector.getBootableImagesData(imageIDs)
    
    def getBaseImagesData(self):
        """
        Devuelve los datos de las imágenes base (i.e. imágenes vanilla)
        """
        return self.__endpointDBConnector.getBaseImagesData()
        
    def getEditedImageIDs(self, userID):
        """
        Devuelve los datos de las imágenes ya asignadas a una asignatura
        que un usuario está editando.
        """
        return self.__endpointDBConnector.getEditedImageIDs(userID)
    
    def getNewImageIDs(self, userID):
        """
        Devuelve los datos de las imágenes no asignadas a ninguna
        asignatura que un usuario está editando.
        """
        return self.__endpointDBConnector.getNewImageIDs(userID)
    
    def getVanillaImageFamilyID(self, imageID):
        return self.__endpointDBConnector.getVanillaImageFamilyID(imageID)
    
    def getVanillaImageFamiliyData(self, vanillaImageFamilyID):
        return self.__endpointDBConnector.getVanillaImageFamilyData(vanillaImageFamilyID)
    
    def getMaxVanillaImageFamilyData(self):
        """
        Calcula los valores máximos del número de CPUs, RAM, disco,... de todas las
        familias de imágenes vanilla
        """
        return self.__endpointDBConnector.getMaxVanillaImageFamilyData()
    
    def getImageRepositoryStatus(self):
        return self.__endpointDBConnector.getImageRepositoryStatus()
    
    def getVirtualMachineServerStatus(self, serverName):
        return self.__endpointDBConnector.getVirtualMachineServerStatus(serverName)
    
    def getOSTypes(self):
        return self.__endpointDBConnector.getOSTypes()
    
    def getOSTypeVariants(self,familyID):
        return self.__endpointDBConnector.getOSTypeVariants(familyID)
    
    def getImageData(self,imageID):
        return self.__endpointDBConnector.getImageData(imageID)
    
if __name__ == "__main__" :
    connector = ClusterConnector(1)
    connector.connectToDatabases("ClusterEndpointDB", "CommandsDB", "connector_user", "CygnusCloud")
    commandID = connector.bootUpVM(1)
    print connector.waitForCommandOutput(commandID)
        