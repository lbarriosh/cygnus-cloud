# -*- coding: utf8 -*-
'''
Conector que usará la web para interactuar con el sistema
@author: Luis Barrios Hernández
@version: 3.5
'''
from database.systemStatusDB.systemStatusDBReader import SystemStatusDatabaseReader
from database.commands.commandsDatabaseConnector import CommandsDatabaseConnector
from clusterServer.connector.commandsHandler import CommandsHandler
from time import sleep

class ClusterServerConnector(object):
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
    
    def connectToDatabases(self, statusDBName, commandsDBName, databaseUser, databasePassword):
        """
        Establece una conexión con las bases de datos de estado y comandos.
        Argumentos:
            statusDBName: el nombre de la base de datos de estado
            commandsDBName: el nombre de la base de datos de comandos
            databaseUser: el nombre de usuario con el que se accederá a las dos bases de datos
            databasePassword: la contraseña para acceder a las bases de datos
        Devuelve:
            Nada
        """
        self.__statusDBConnector = SystemStatusDatabaseReader(databaseUser, databasePassword, statusDBName)
        self.__statusDBConnector.connect()
        self.__commandsDBConnector = CommandsDatabaseConnector(databaseUser, databasePassword, commandsDBName, 1)
        self.__commandsDBConnector.connect()
        
    def dispose(self):
        """
        Cierra las conexiones con las bases de datos
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        self.__statusDBConnector.disconnect()
        self.__commandsDBConnector.disconnect()
        
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
        return self.__statusDBConnector.getActiveVMsData(userID)
    
    def getVMDistributionData(self):
        """
        Devuelve los datos de distribución de las imágenes
        Argumentos:
            Ninguno
        Devuelve: una lista de diccionarios con los datos de distribución de las imágenes
        """
        return self.__statusDBConnector.getVMDistributionData()
        
    def getVMServersData(self):
        """
        Devuelve los datos básicos de los servidores de máquinas virtuales
        Argumentos:
            Ninguno
        Devuelve: una lista de diccionarios con los datos básicos de los servidores de máquinas virtuales
        """
        return self.__statusDBConnector.getVMServersData()
        
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
        (commandType, commandArgs) = CommandsHandler.createVMServerRegistrationCommand(vmServerIP, vmServerPort, vmServerName, isVanillaServer)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
        
    def unregisterVMServer(self, vmServerNameOrIP, halt):
        """
        Borra un servidor de máquinas virtuales
        Argumentos:
            vmServerNameOrIP: el nombre o la IP del servidor a borrar
            halt: si es True, el servidor se apagará inmediatamente. Si es False, esperará a que los usuarios apaguen sus
            máquinas virtuales.
        Devuelve:
            El identificador único del comando.
            @attention: La representación del identificador único del comando puede cambiar sin previo aviso.
        """
        (commandType, commandArgs) = CommandsHandler.createVMServerUnregistrationOrShutdownCommand(True, vmServerNameOrIP, halt)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def shutdownVMServer(self, vmServerNameOrIP, halt):
        """
        Apaga un servidor de máquinas virtuales
        Argumentos:
            vmServerNameOrIP: el nombre o la IP del servidor a borrar
            halt: si es True, el servidor se apagará inmediatamente. Si es False, esperará a que los usuarios apaguen sus
            máquinas virtuales.
        Devuelve:
            El identificador único del comando.
            @attention: La representación del identificador único del comando puede cambiar sin previo aviso.
        """
        (commandType, commandArgs) = CommandsHandler.createVMServerUnregistrationOrShutdownCommand(False, vmServerNameOrIP, halt)
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
        (commandType, commandArgs) = CommandsHandler.createVMServerBootCommand(vmServerNameOrIP)
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
        (commandType, commandArgs) = CommandsHandler.createVMBootCommand(imageID, self.__userID)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def halt(self, haltVMServers):
        """
        Apaga toda la infraestructura
        Argumentos:
            haltVMServers: si es True, el servidor se apagará inmediatamente. Si es False, esperará a que los usuarios apaguen sus
            máquinas virtuales.
        Devuelve: 
            Nada
        """
        (commandType, commandArgs) = CommandsHandler.createHaltCommand(haltVMServers)
        self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
        
    def destroyDomain(self, domainID):
        """
        Destruye una máquina virtual
        Argumentos:
            domainID: el identificador único de la máquina virtual a destruir
        Devuelve:
            Nada
        """
        (commandType, commandArgs) = CommandsHandler.createDomainDestructionCommand(domainID)
        return self.__commandsDBConnector.addCommand(self.__userID, commandType, commandArgs)
    
    def changeVMServerConfiguration(self, serverNameOrIPAddress, newName, newIPAddress, newPort, 
                                    newVanillaImageEditionBehavior):
        (commandType, commandArgs) = CommandsHandler.createVMServerConfigurationChangeCommand(serverNameOrIPAddress, 
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
                result = CommandsHandler.deserializeCommandOutput(outputType, outputContent)
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
            return CommandsHandler.deserializeCommandOutput(result[0], result[1])
    
if __name__ == "__main__":
    connector = ClusterServerConnector(1)
    connector.connectToDatabases("SystemStatusDB", "CommandsDB", "website", "CygnusCloud")
    sleep(3)
    commandID = connector.changeVMServerConfiguration("Server2", "Foo", "192.168.0.1", 15900, 
                                    True)
    print connector.waitForCommandOutput(commandID)
    sleep(4)
    print connector.getVMServersData()
    connector.halt(True)
    connector.dispose()    