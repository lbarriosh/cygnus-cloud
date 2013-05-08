# -*- coding: UTF8 -*-

from ccutils.enums import enum
from database.utils.connector import BasicDatabaseConnector
import time

SERVER_STATE_T = enum("BOOTING", "READY", "SHUT_DOWN", "RECONNECTING", "CONNECTION_TIMED_OUT")

IMAGE_STATE_T = enum("READY", "EDITED", "DEPLOY", "DELETE")

class ClusterServerDatabaseConnector(BasicDatabaseConnector):
    """
    Nota: esta clase es ServerVMManager, con los métodos específicos
    de ImagesInServerManager.
    """
    '''
        These objects register and delete virtual machine servers to the database.   
    '''    

    def __init__(self, sqlUser, sqlPassword, databaseName):
        '''
            Constructor de la clase. Recibe el nombre y lla contrasennia del usuario sql encargado
            de gestionar la base de datos
            Argumentos:
                sqlUser: usuario para conectarnos a MySQL
                sqlPassword: contraseña para conectarnos a MySQL
                databaseName: nombre de la base de datos a la que nos vamos a conectar
            Devuelve:
                Nada
        '''
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPassword, databaseName)
        
    def deleteVMServerStatistics(self, serverID):
        '''
        Borra las estadísticas de un servidor de máquinas virtuales
            Argumentos:
                serverId: el identificador único del servidor
            Devuelve:
                Nada
        '''
        command = "DELETE FROM VMServerStatus WHERE serverId = {0}".format(serverID)
        self._executeUpdate(command)
        command = "DELETE FROM AllocatedVMServerResources WHERE serverID = {0};".format(serverID)
        self._executeUpdate(command)
        
    def getVMServerBasicData(self, serverId):
        '''
            Devuelve la información asociada a un servidor de máquinas virtuales
            Argumentos:
                serverId: el identificador único del servidor
            Devuelve:
                Diccionario con los datos del servidor
                Nota: ¿por qué no una tupla o una lista? Porque el orden en que se devuelven
                las cosas importaría, lo cual es un fastidio para añadir y quitar cosas
                (lo sé por la red). Al devolver un diccionario, es mucho más fácil añadir
                y quitar cosas a devolver.
        '''
        #Creamos la consulta encargada de extraer los datos
        query = "SELECT serverName, serverStatus, serverIP, serverPort, isVanillaServer FROM VMServer"\
            + " WHERE serverId = '{0}';".format(serverId)
        # Recogemos los resultados
        result = self._executeQuery(query, True)
        if (result == None) : 
            return None
        d = dict()
        (name, status, ip, port, isVanillaServer) = result
        # Devolvemos el resultado 
        d["ServerName"] = name
        d["ServerStatus"] = status
        d["ServerIP"] = ip
        d["ServerPort"] = port
        d["IsVanillaServer"] = isVanillaServer == 1
        return d         
        
    def getVMServerStatistics(self, serverID) :
        '''
            Devuelve las estadísticas de un servidor de máquinas virtuales
            Argumentos:
                serverId: el identificador único del servidor
            Returns:
                Diccionario con las estadísticas del servidor.
        '''
        #Creamos la consulta encargada de extraer los datos
        query = "SELECT hosts, ramInUse, ramSize, freeStorageSpace, availableStorageSpace,\
            freeTemporarySpace, availableTemporarySpace, activeVCPUs, physicalCPUs FROM VMServerStatus WHERE serverId = {0};".format(serverID)
        result = self._executeQuery(query, True)
        if (result == None) : 
            return None            
        d = dict()        
        d["ActiveHosts"] = int(result[0])
        d["RAMInUse"] = int(result[1])
        d["RAMSize"] = int(result[2])
        d["FreeStorageSpace"] = int(result[3])
        d["AvailableStorageSpace"] = int(result[4])
        d["FreeTemporarySpace"] = int(result[5])
        d["AvailableTemporarySpace"] = int(result[6])
        d["ActiveVCPUs"] = int(result[7])
        d["PhysicalCPUs"] = int(result[8])
        
        query = "SELECT SUM(ramInUse), SUM(freeStorageSpace), SUM(freeTemporarySpace), SUM(activeVCPUs), SUM(activeHosts) FROM AllocatedVMServerResources \
            WHERE serverId = {0};".format(serverID)
        result = self._executeQuery(query, True)
        if (result[0] != None) :
            d["RAMInUse"] += int(round(result[0]))
            d["FreeStorageSpace"] -= int(round(result[1]))
            d["FreeTemporarySpace"] -= int(round(result[2]))
            d["ActiveVCPUs"] += int(round(result[3]))
            d["ActiveHosts"] += int(round(result[3]))
        
        # Devolvemos los resultados
        return d
    
    def getVMServerIDs(self):
        '''
            Permite obtener una lista con los identificadores de todos los servidores de 
            máquinas virtuales que actualmente se encuentran dados de alta en la base de datos.
        
            Nota: este es el antiguo método getServers
            Argumentos: 
                Ninguno
            Devuelve:
                Lista con los identificadores de todos los servidores de máquinas virtuales
        '''
        #Creamos la consulta encargada de extraer los datos
        query = "SELECT serverId FROM VMServer;"  
        #Recogemos los resultado
        results=self._executeQuery(query)
        if (results == None) :
            return []
        serverIds = []
        for r in results:
            serverIds.append(r)
        #Devolvemos la lista resultado
        return serverIds
    
    def getActiveVMServersConnectionData(self):
        """
        Returns a list containing the active servers' IP addresses.
        Args:
            None
        Returns: 
            Nothing
        """
        query = "SELECT serverIP, serverPort FROM VMServer WHERE serverStatus = " + str(SERVER_STATE_T.READY) + ";"
        results = self._executeQuery(query)
        if (results == None) :
            return []
        serverIPs = []
        for r in results :
            serverIPs.append({"ServerIP" : r[0], "ServerPort" : r[1]})
        return serverIPs
        
        
    def registerVMServer(self, name, IPAddress, port, isVanillaServer):
        '''
            Permite registrar un Nuevo servidor de máquinas virtuales con el puerto, la IP y el número
             máximo de máquinas virtuales que se le pasan como argumento
            Argumentos:
                name: nombre del nuevo servidor
                IPAddress: la IP del nuevo servidor
                port: el puerto del nuevo servidor
                isVanillaServer: True si el servidor de máquinas virtuales se usará preferentemente
                    para albergar imágenes vanilla, y false en caso contrario.
            Returns:
                El identificador del nuevo servidor.
            Nota: creo que es mejor el nombre registerVMServer. subscribe significa suscribir,
            ratificar algo.
        '''
        if (isVanillaServer) :
            vanillaValue = 1
        else :
            vanillaValue = 0
        
        update = "INSERT INTO VMServer(serverStatus, serverName, serverIP, serverPort, isVanillaServer) VALUES ({0}, '{1}', '{2}', {3}, {4});"\
            .format(SERVER_STATE_T.BOOTING, name, IPAddress, port, vanillaValue)
        self._executeUpdate(update)      
        query = "SELECT serverId FROM VMServer WHERE serverIP ='" + IPAddress + "';"
        serverId = self._executeQuery(query)[-1]
        return serverId
    
    def deleteVMServer(self, serverNameOrIPAddress):
        '''
            Permite eliminar un determinado servidor de máquinas virtuales de la base de datos cuyo
             identificador se le pasa como argumento.
            Argumentos:
                serverNameOrIPAddress: el nombre o la IP del servidor
            Devuelve:
                Nada
            Nota: tuve que dejar de usar el id porque la web no sabe que ids tiene asignado
            cada servidor. Estos son únicos dentro del servidor principal.
        '''
        serverId = self.getVMServerID(serverNameOrIPAddress)
        # Borramos la fila
        query = "DELETE FROM VMServer WHERE serverId = " + str(serverId) + ";"
        #Ejecutamos el comando
        self._executeUpdate(query)
        # Apaño. ON DELETE CASCADE no funciona cuando las tablas usan un motor de almacenamiento
        # distinto. Una usa INNODB (VMServer) y otra usa MEMORY (VMServerStatus, que es nueva)
        self.deleteVMServerStatistics(serverId)
        
    def getImageIDs(self):
        query = "SELECT DISTINCT imageId FROM ImageOnServer;"
        results = self._executeQuery(query)
        imageIDs = []
        for r in results:
            imageIDs.append(r)
        return imageIDs
        
    def getHosts(self, imageId, imageStatus = IMAGE_STATE_T.READY):
        '''
            Devuelve una lista con todos los identificadores de servidores que pueden dar acceso a la
             imagen cuyo identificador se pasa como argumento.
            Argumentos:
                imageId: el identificador único de la imagen
            Devuelve:
                lista con los identificadores de los servidores que tienen la imagen
            Nota: tuve que añadir el estado de los servidores de máquinas virtuales, que no
            estaba contemplado en el diseño inicial. Y tengo que cruzar dos tablas: una imagen
            no está disponible si un servidor que no está preparado, que está apagado o que
            se ha desconectado la tiene. Sólo está disponible si el servidor está listo.
        '''
        # Creamos la consulta
        query = "SELECT ImageOnServer.serverId FROM ImageOnServer\
            INNER JOIN VMServer ON ImageOnServer.serverId = VMServer.serverID \
                WHERE VMServer.serverStatus = {0} AND imageId = {1} AND status = {2};".format(SERVER_STATE_T.READY, imageId, imageStatus) 
        #Recogemos los resultado
        results=self._executeQuery(query)
        if (results == None) :
            return []
        return results
    
    def resetVMServersStatus(self):
        vmServerIDs = self.getVMServerIDs()
        for vmServerID in vmServerIDs :
            self.updateVMServerStatus(vmServerID, SERVER_STATE_T.SHUT_DOWN)
    
    def getHostedImages(self, serverID):
        '''
            Devuelve la lista de máquinas virtuales que puede albergar el servidor de máquinas virtuales
            cuyo identificador nos proporcionan como argumento.
            Argumentos:
                imageId: el identificador único de la imagen
            Devuelve:
                lista con los identificadores de los servidores que tienen la imagen
        '''
        # Creamos la consulta
        query = "SELECT VMServer.serverName, imageId, status FROM VMServer, ImageOnServer " +\
                 "WHERE VMServer.serverId = ImageOnServer.serverId AND VMServer.serverID = {0};"\
                 .format(serverID)
        #Recogemos los resultado
        results=self._executeQuery(query)
        if (results == None) :
            return []
        #Guardamos en una lista los ids resultantes
        retrievedData = []
        for r in results:
            retrievedData.append({"ServerName" : str(r[0]), "VMID" : int(r[1]), "Status": int(r[2])})
        #Devolvemos la lista resultado
        return retrievedData
    
    def hostsImage(self, serverID, imageID):
        query = "SELECT * FROM ImageOnServer WHERE serverId = {0} AND imageID = {1};".format(serverID, imageID)
        result = self._executeQuery(query, True)
        return result != None
    
    def getVMServerID(self, nameOrIPAddress):
        '''
        Devuelve el ID de un servidor de máquinas virtuales a partir de su nombre o
        su IP.
        Argumentos:    
            nameOrIPAddress: el nombre o la IP del servidor de máquinas virtuales
        Devuelve:
            El ID del servidor.
        '''
        query = "SELECT serverId FROM VMServer WHERE serverIP = '" + nameOrIPAddress +\
             "' OR serverName = '" + nameOrIPAddress + "';"
        # Execute it
        results=self._executeQuery(query, True)
        if (results == None) : 
            return None
        return results
    
    def updateVMServerStatus(self, serverId, newStatus):
        '''
            Actualiza el estado de un servidor de máquinas virtuales (listo, arrancando,
            desconectado,...)
            Argumentos:
                serverId: el identificador úncio del servidor
                newStatus: el nuevo estado del servidor
            Devuelve:
                Nada
        '''
        command = "UPDATE VMServer SET serverStatus=" + str(newStatus) + \
            " WHERE serverId = " + str(serverId) + ";"
        # Execute it
        self._executeUpdate(command)
        
        
    def getServerImages(self, serverId):
        '''
            Devuelve una lista con los identificadores de las imágenes asociadas a un servidor 
              de máquinas virtuales.
            Argumentos:
                serverId: el identificador del servidor de máquinas virtuales
            Returns:
                Lista con los identificadores de las imágenes
            Nota: este método está modificado para que un solo objeto me sirva para 
            leer la base de datos. Tal y como estaba, tenía que tener un objeto ImageServerManager
            para cada servidor de máquinas virtuales, y eso son muchas conexiones.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT imageId, status FROM ImageOnServer WHERE serverId = {0}; ".format(serverId)    
        #Recogemos los resultado
        results=self._executeQuery(sql)
        #Guardamos en una lista los ids resultantes
        serverIds = []
        for r in results:
            serverIds.append((r[0], r[1]))
        #Devolvemos la lista resultado
        return serverIds
         
    def assignImageToServer(self, serverID, imageID):
        '''
        Asigna una imagen a un servidor de máquinas virtuales
        Argumentos:
            serverID: identificador único del servidor de máquinas virtuales
            imageID: identificador único de la imagen
        Devuelve:
            Nada.
        '''
        # Insert the row in the table
        query = "INSERT INTO ImageOnServer VALUES({0}, {1}, {2});".format(serverID, imageID, IMAGE_STATE_T.READY)
        self._executeUpdate(query)
        
    def deleteImageFromServer(self, serverID, imageID):
        update = "DELETE FROM ImageOnServer WHERE serverId = {0} AND imageId = {1}".format(serverID, imageID)
        self._executeUpdate(update)
        
    def setVMServerStatistics(self, serverID, runningHosts, ramInUse, ramSize, freeStorageSpace,
                              availableStorageSpace, freeTemporarySpace, availableTemporarySpace,
                              activeVCPUs, physicalCPUs):
        '''
        Actualiza las estadísticas de un servidor de máquinas virtuales.
        Argumentos
        '''
        query = "INSERT INTO VMServerStatus VALUES({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9});".format(serverID, runningHosts, 
            ramInUse, ramSize, freeStorageSpace, availableStorageSpace, freeTemporarySpace, availableTemporarySpace,
                              activeVCPUs, physicalCPUs)
        try :
            self._executeUpdate(query)
        except Exception :
            query = "UPDATE VMServerStatus SET hosts = {0}, ramInUse = {1}, ramSize = {2}, freeStorageSpace = {3},\
                availableStorageSpace = {4}, freeTemporarySpace = {5}, availableTemporarySpace = {6},\
                activeVCPUs = {7}, physicalCPUs = {8}  WHERE serverId = {9};".format(runningHosts, ramInUse, ramSize, freeStorageSpace,
                              availableStorageSpace, freeTemporarySpace, availableTemporarySpace,
                              activeVCPUs, physicalCPUs, serverID)
            self._executeUpdate(query)
        
        update = "DELETE FROM AllocatedVMServerResources WHERE serverID = {0} AND remove = 1;".format(serverID)
        self._executeUpdate(update)
            
            
        
    def setServerBasicData(self, serverId, name, status, IPAddress, port, isVanillaServer):
        '''
            Modifica los datos básicos de un servidor de máquinas virtuales
            Argumentos:
                name: nuevo nombre del servidor
                status: nuevo estado del servidor
                IPAddress: nueva IP del servidor
                port: nuevo puerto del servidor
                isVanillaServer: indica si el servidor se usará preferentemente para editar imágenes o no
            Devuelve:
                Nada
        '''
        if (isVanillaServer) : vanillaValue = 1
        else : vanillaValue = 0
        
        query = "UPDATE VMServer SET serverName = '{0}', serverIP = '{1}', serverPort = {2}, serverStatus = {3}, isVanillaServer = {4}\
            WHERE serverID = {5};".format(name, IPAddress, port, status, vanillaValue, serverId);
        
        self._executeUpdate(query)
        
    def registerVMBootCommand(self, commandID, vmID):
        """
        Registers a virtual machine boot command in the database.
        Args:
            commandID: the virtual machine boot command's unique identifier
        Returns:
            Nothing
        """
        timestamp = time.time()
        update = "INSERT INTO VMBootCommand VALUES ('{0}', {1}, {2});".format(commandID, timestamp, vmID)
        self._executeUpdate(update)
        
    def removeVMBootCommand(self, commandID):
        """
        Removes a virtual machine boot command from the database
        Args:
            commandID: the command's unique identifier
        Returns:
            Nothing
        """
        update = "DELETE FROM VMBootCommand WHERE commandID = '{0}';".format(commandID)        
        self._executeUpdate(update)
        
    def getOldVMBootCommandID(self, timeout):
        """
        Removes an old virtual machine command id from the database and returns it.
        Args:
            the timeout. A command will be considered old when its timestamp plus timeout
            is greater than or equal to the current time.
        Returns:
            If an old commandID is found, it will be returned. Otherwise, None will be returned
        """
        query = "SELECT * FROM VMBootCommand;"
        results = self._executeQuery(query, False)
        if (results == None) :
            return None
        currentTime = time.time()
        for row in results :
            difference = currentTime - row[1]
            if (difference >= timeout) :
                update = "DELETE FROM VMBootCommand WHERE commandID = '{0}'".format(row[0])
                self._executeUpdate(update)
                return (row[0], int(row[2])) # Match! -> return it
        return None
    
    def getVMBootCommandData(self, commandID):
        query = "SELECT * FROM VMBootCommand WHERE commandID = '{0}';".format(commandID)
        result = self._executeQuery(query, True)
        if (result == None) : return None
        else :
            return (result[0], int(result[2]))
    
    def registerActiveVMLocation(self, vmID, serverID):
        """
        Registra la ubicación de una nueva máquina virtual activa
        Argumentos:
            vmID: el identificador único de la máquina virtual
            serverID: el identificador único del servidor de máquinas virtuales
            que la alberga.
        Devuelve:
            nada
        """
        update = "INSERT INTO ActiveVMDistribution VALUES ('{0}',{1});".format(vmID, serverID)
        self._executeUpdate(update)
        
    def deleteActiveVMLocation(self, vmID):
        """
        Elimina la ubicación de una máquina virtual activa
        Argumentos:
            vmID: el identificador único de la máquina virtual
        Devuelve:
            nada
        """
        update = "DELETE FROM ActiveVMDistribution WHERE vmID = '{0}';".format(vmID);
        self._executeUpdate(update)
        
    def getActiveVMHostID(self, vmID):
        """
        Devuelve la ubicación de una máquina virtual activa
        Argumentos:
            vmID: el identificador único de la máquina virtual
        Devuelve:
            El identificador único del servidor de máquinas virtuales 
            que alberga la máquina virtual
        """
        query = "SELECT serverID FROM ActiveVMDistribution WHERE vmID = '{0}';".format(vmID)
        result = self._executeQuery(query, True)
        if result == None :
            return None
        else :
            return result
        
    def getReadyVanillaServers(self):
        query = "SELECT serverID FROM VMServer WHERE isVanillaServer = 1 AND serverStatus = {0};".format(SERVER_STATE_T.READY)
        result = self._executeQuery(query, False)
        if (result == None) :
            return []
        else :
            return result
    
    def deleteHostedVMs(self, serverID):
        """
        Borra la ubicación de todas las máquinas virtuales activas registradas en un servidor
        de máquinas virtuales.
        Argumentos:
            serverID: el identificador único del servidor de máquinas virtuales
        Devuelve:
            Nada
        """
        update = "DELETE FROM ActiveVMDistribution WHERE serverID = {0};".format(serverID)
        self._executeUpdate(update)
        
    def registerHostedVMs(self, serverID, hostedVMs):
        """
        Registra un conjunto de máquinas virtuales almacenadas en un servidor
        """
        update = "DELETE FROM ActiveVMDistribution WHERE serverID = {0};".format(serverID)
        self._executeUpdate(update)
        update = "INSERT INTO ActiveVMDistribution VALUES ('{0}',{1});"
        for hostedDomainUID in hostedVMs :
            self._executeUpdate(update.format(hostedDomainUID, serverID))
            
    def getVanillaImageFamilyFeatures(self, family):
        """
        Devuelve los datos de una imagen vanilla
        Argumentos:
    family imageID: ID de la imagen vanilla
        Devuelve:
            Un diccionario con los datos de la imagen, con las siguientes claves:
                RAM
                vCPUs
                OSDiskSize
                dataDiskSize
        """
        query = "SELECT ramSize, vCPUs, osDiskSize, dataDiskSize FROM VanillaImageFamily WHERE familyID = {0}".format(family)
        # Ejecutamos la consulta
        results=self._executeQuery(query)
        if (results == ()) : 
            return None
        (ram, vCPUs, OSDiskSize, dataDiskSize) = results[0]
        # Creamos el diccionario con los datos
        d = dict() 
        d["RAMSize"] = ram
        d["vCPUs"] = vCPUs
        d["osDiskSize"] = OSDiskSize
        d["dataDiskSize"] = dataDiskSize
        return d
    
    def addVanillaImageFamily(self, familyName, RAMSize, vCPUs, osDiskSize, dataDiskSize):
        update = "INSERT INTO VanillaImageFamily(familyName, ramSize, vCPUs, osDiskSize, dataDiskSize) VALUES ('{0}', {1}, {2}, {3}, {4});"\
            .format(familyName, RAMSize, vCPUs, osDiskSize, dataDiskSize)
        self._executeUpdate(update)
        
    def getVanillaImageFamilyID(self, familyName):
        query = "SELECT familyID FROM VanillaImageFamily WHERE familyName = '{0}';".format(familyName)
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            return int(result)
        
    def deleteVanillaImageFamilies(self):
        update = "DELETE FROM VanillaImageFamily;"
        self._executeUpdate(update)
    
    def getVMResources(self, VMID):
        """
        Devuelve los recursos de una imagen
        Argumentos:
            VMID: ID de la imagen
        Devuelve:
            Un diccionario con los datos de la imagen, con las siguientes claves:
                RAM
                vCPUs
                OSDiskSize
                dataDiskSize
        """
        # Conseguimos el ID de la imagen vanilla en la que está basada
        query = "SELECT * FROM VMfromVanilla WHERE familyID = {0}".format(VMID)
        # Ejecutamos la consulta
        results=self._executeQuery(query)
        if (results == ()) : 
            return None
        (vanillaID, VMID) = results
        return self.getVanillaImageFamilyFeatures(vanillaID)
    
    def getFamilyID(self, imageID):
        query = "SELECT familyID FROM VanillaImageFamilyOf WHERE imageID = {0};".format(imageID)
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            return int(result)
        
    def registerFamilyID(self, imageID, familyID):
        update = "INSERT INTO VanillaImageFamilyOf VALUES ({0}, {1});".format(imageID, familyID)
        self._executeUpdate(update)
        
    def deleteFamilyID(self, imageID):
        update = "DELETE FROM VanillaImageFamilyOf WHERE imageID = {0}".format(imageID)
        self._executeUpdate(update)
        
    def addImageRepository(self, repositoryIP, repositoryPort, status):
        command = "INSERT INTO ImageRepository VALUES ('{0}', {1}, 0, 0, {2})".format(repositoryIP, repositoryPort, status)
        self._executeUpdate(command)
        
    def updateImageRepositoryStatus(self, repositoryIP, repositoryPort, freeDiskSpace, availableDiskSpace):
        command = "UPDATE ImageRepository SET freeDiskSpace={2}, availableDiskSpace={3} WHERE repositoryIP = '{0}' AND repositoryPort = {1};"\
            .format(repositoryIP, repositoryPort, freeDiskSpace, availableDiskSpace)
        self._executeUpdate(command)
        command = "DELETE FROM AllocatedImageRepositoryResources WHERE repositoryIP = '{0}' AND repositoryPort = {1} AND remove = 1".format(repositoryIP, repositoryPort)
        self._executeUpdate(command)
        
    def updateImageRepositoryConnectionStatus(self, repositoryIP, repositoryPort, status):
        command = "UPDATE ImageRepository SET connection_status={2} WHERE repositoryIP = '{0}' AND repositoryPort = {1};"\
            .format(repositoryIP, repositoryPort, status)
        self._executeUpdate(command)
        
    def getImageRepositoryStatus(self, repositoryIP, repositoryPort):
        query = "SELECT freeDiskSpace, availableDiskSpace, connection_status FROM ImageRepository WHERE repositoryIP = '{0}' AND repositoryPort = {1};"\
            .format(repositoryIP, repositoryPort)
        result = self._executeQuery(query, True)
        if (result == None or result[2] != SERVER_STATE_T.READY):
            return None
        query = "SELECT SUM(allocatedDiskSpace) FROM AllocatedImageRepositoryResources WHERE repositoryIP = '{0}' AND repositoryPort={1};".\
            format(repositoryIP, repositoryPort)
        allocatedSpace = self._executeQuery(query, True)
        status =  {"FreeDiskSpace" : result[0], "AvailableDiskSpace" : result[1], "ConnectionStatus" : result[2]}
        if (allocatedSpace != None) :
            status["FreeDiskSpace"] += round(allocatedSpace[0])
        return status
        
    def allocateImageRepositoryResources(self, repositoryIP, repositoryPort, commandID, diskSpace):
        update = "INSERT INTO AllocatedImageRepositoryResources VALUES ('{0}', '{1}', {2}, {3}, 0)".format(commandID, repositoryIP, repositoryPort, diskSpace)
        self._executeUpdate(update)
        
    def freeImageRepositoryResources(self, commandID, error):
        if (error) :
            update = "DELETE FROM AllocatedImageRepositoryResources WHERE commandID = '{0}';".format(commandID)
        else :
            update = "UPDATE AllocatedImageRepositoryResources SET remove = 1 WHERE commandID = '{0}';".format(commandID)
        self._executeUpdate(update)
        
    def registerNewVMVanillaImageFamily(self, commandID, familyID):
        update = "INSERT INTO VanillaImageFamilyOfNewVM VALUES ('{0}', {1});".format(commandID, familyID)
        self._executeUpdate(update)
        
    def getNewVMVanillaImageFamily(self, commandID):
        query = "SELECT familyID FROM VanillaImageFamilyOfNewVM WHERE temporaryID = '{0}';".format(commandID)
        return self._executeQuery(query, True)
        
    def deleteNewVMVanillaImageFamily(self, commandID):
        update = "DELETE FROM VanillaImageFamilyOfNewVM WHERE temporaryID = '{0}';".format(commandID)
        self._executeUpdate(update)
        
    def addImageEditionCommand(self, commandID, imageID):
        self.__addImageCommand("ImageEditionCommand", commandID, imageID)
        
    def addImageDeletionCommand(self, commandID, imageID):
        self.__addImageCommand("ImageDeletionCommand", commandID, imageID)
        
    def __addImageCommand(self, tableName, commandID, imageID):
        update = "INSERT INTO {0} VALUES('{1}', {2});".format(tableName, commandID, imageID)
        self._executeUpdate(update)
        
    def removeImageEditionCommand(self, commandID):
        self.__removeImageCommand("ImageEditionCommand", commandID)
        
    def removeImageDeletionCommand(self, commandID):
        self.__removeImageCommand("ImageDeletionCommand", commandID)
        
    def __removeImageCommand(self, tableName, commandID):
        update = "DELETE FROM {0} WHERE commandID = '{1}';".format(tableName, commandID)
        self._executeUpdate(update)
        
    def isImageEditionCommand(self, commandID):
        return self.__classifyCommand("ImageEditionCommand", commandID)
    
    def isImageDeletionCommand(self, commandID):
        return self.__classifyCommand("ImageDeletionCommand", commandID)
        
    def __classifyCommand(self, tableName, commandID):
        query = "SELECT * FROM {0} WHERE commandID = '{1}';".format(tableName, commandID)
        return self._executeQuery(query, True) != None
    
    def isBeingEdited(self, imageID):
        return self.__isAffectedByCommand("ImageEditionCommand", imageID)
    
    def isBeingDeleted(self, imageID):
        return self.__isAffectedByCommand("ImageDeletionCommand", imageID)
    
    def __isAffectedByCommand(self, tableName, imageID):
        query = "SELECT * FROM {0} WHERE imageID = {1}".format(tableName, imageID)
        return self._executeQuery(query, True) != None
    
    def getImageEditionCommandID(self, imageID):
        return self.__getCommandID("ImageEditionCommand", imageID)
        
    def getImageDeletionCommandID(self, imageID):
        return self.__getCommandID("ImageDeletionCommand", imageID)
    
    def __getCommandID(self, table, imageID):
        query = "SELECT commandID FROM {0} WHERE imageID = {1};".format(table, imageID)
        return self._executeQuery(query, True)    
    
    def changeImageStatus(self, imageID, status):
        update = "UPDATE ImageOnServer SET status = {1} WHERE imageId = {0}".format(imageID, status)
        self._executeUpdate(update)
        
    def changeImageCopyStatus(self, imageID, serverID, status):
        update = "UPDATE ImageOnServer SET status = {2} WHERE imageId = {0} AND serverId = {1}".format(imageID, serverID, status)
        self._executeUpdate(update)      
        
    def isThereSomeImageCopyInState(self, imageID, state):
        query = "SELECT * FROM ImageOnServer WHERE imageID = {0} AND status = {1};".format(imageID, state)
        return self._executeQuery(query, True) != None
    
    def getHostedImagesWithStatus(self, serverID, status):
        query = "SELECT imageId FROM ImageOnServer WHERE serverId = {0} AND status = {1};".format(serverID, status)
        result = self._executeQuery(query, False)
        if (result == None) : 
            return []
        else :
            return result
        
    def allocateVMServerResources(self, commandID, serverID, ramInUse, freeStorageSpace, freeTemporarySpace, activeVCPUs, activeHosts):
        update = "INSERT INTO AllocatedVMServerResources VALUES('{0}', {1}, {2}, {3}, {4}, {5}, {6}, 0);"\
            .format(commandID, serverID, ramInUse, freeStorageSpace, freeTemporarySpace, activeVCPUs, activeHosts)
        self._executeUpdate(update)
        
    def freeVMServerResources(self, commandID, error):
        if (error) :
            update = "DELETE FROM AllocatedVMServerResources WHERE commandID = '{0}';".format(commandID)
        else :
            update = "UPDATE AllocatedVMServerResources SET remove = 1 WHERE commandID = '{0}';".format(commandID)
        self._executeUpdate(update)
    