# -*- coding: UTF8 -*-

from ccutils.enums import enum
from database.utils.connector import BasicDatabaseConnector
import time

SERVER_STATE_T = enum("BOOTING", "READY", "SHUT_DOWN", "RECONNECTING", "CONNECTION_TIMED_OUT")

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
        
    def deleteVMServerStatistics(self, serverId):
        '''
        Borra las estadísticas de un servidor de máquinas virtuales
            Argumentos:
                serverId: el identificador único del servidor
            Devuelve:
                Nada
        '''
        command = "DELETE FROM VMServerStatus WHERE serverId = " + str(serverId)
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
        
    def getVMServerStatistics(self, serverId) :
        '''
            Devuelve las estadísticas de un servidor de máquinas virtuales
            Argumentos:
                serverId: el identificador único del servidor
            Returns:
                Diccionario con las estadísticas del servidor.
        '''
        #Creamos la consulta encargada de extraer los datos
        query = "SELECT hosts, ramInUse, ramSize, freeStorageSpace, availableStorageSpace,\
            freeTemporarySpace, availableTemporarySpace, activeVCPUs, physicalCPUs FROM VMServerStatus WHERE serverId = " + str(serverId) + ";"
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
        query = "DELETE From VMServerStatus WHERE serverId = " + str(serverId) + ";"
        self._executeUpdate(query)
        
    def getImageIDs(self):
        query = "SELECT DISTINCT imageId FROM ImageOnServer;"
        results = self._executeQuery(query)
        imageIDs = []
        for r in results:
            imageIDs.append(r)
        return imageIDs
        
    def getHosts(self, imageId):
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
        query = "SELECT ImageOnServer.serverId FROM ImageOnServer " +\
            "INNER JOIN VMServer ON ImageOnServer.serverId = VMServer.serverID " \
                + "WHERE VMServer.serverStatus = " + str(SERVER_STATE_T.READY) \
                + " AND " + "imageId =" + str(imageId) + ";"
        #Recogemos los resultado
        results=self._executeQuery(query)
        if (results == None) :
            return []
        #Guardamos en una lista los ids resultantes
        serverIds = []
        for r in results:
            serverIds.append(r)
        #Devolvemos la lista resultado
        return serverIds
    
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
        query = "SELECT VMServer.serverName, imageId FROM VMServer, ImageOnServer " +\
                 "WHERE VMServer.serverId = ImageOnServer.serverId AND VMServer.serverID = {0};"\
                 .format(serverID)
        #Recogemos los resultado
        results=self._executeQuery(query)
        #Guardamos en una lista los ids resultantes
        retrievedData = []
        for r in results:
            retrievedData.append({"ServerName" : r[0], "VMID" : int(r[1])})
        #Devolvemos la lista resultado
        return retrievedData
    
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
        query = "UPDATE VMServer SET serverStatus=" + str(newStatus) + \
            " WHERE serverId = " + str(serverId) + ";"
        # Execute it
        self._executeUpdate(query)
        
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
        sql = "SELECT imageId FROM ImageOnServer WHERE serverId = " + str(serverId)    
        #Recogemos los resultado
        results=self._executeQuery(sql)
        #Guardamos en una lista los ids resultantes
        serverIds = []
        for r in results:
            serverIds.append(r)
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
        query = "INSERT INTO ImageOnServer VALUES(" + str(serverID)+ "," + str(imageID)  +") "  
        self._executeUpdate(query)
        
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
        
    def addImageRepository(self, repositoryIP, repositoryPort, status):
        command = "INSERT INTO ImageRepository VALUES ('{0}', {1}, 0, 0, {2})".format(repositoryIP, repositoryPort, status)
        self._executeUpdate(command)
        
    def updateImageRepositoryStatus(self, repositoryIP, repositoryPort, freeDiskSpace, availableDiskSpace):
        command = "UPDATE ImageRepository SET freeDiskSpace={2}, availableDiskSpace={3} WHERE repositoryIP = '{0}' AND repositoryPort = {1};"\
            .format(repositoryIP, repositoryPort, freeDiskSpace, availableDiskSpace)
        self._executeUpdate(command)
        
    def updateImageRepositoryConnectionStatus(self, repositoryIP, repositoryPort, status):
        command = "UPDATE ImageRepository SET connection_status={2} WHERE repositoryIP = '{0}' AND repositoryPort = {1};"\
            .format(repositoryIP, repositoryPort, status)
        self._executeUpdate(command)
        
    def getImageRepositoryStatus(self, repositoryIP, repositoryPort):
        query = "SELECT freeDiskSpace, availableDiskSpace, connection_status FROM ImageRepository WHERE repositoryIP = '{0}' AND repositoryPort = {1};"\
            .format(repositoryIP, repositoryPort)
        result = self._executeQuery(query, True)
        if (result == None):
            return None
        else :
            return {"FreeDiskSpace" : result[0], "AvailableDiskSpace" : result[1], "ConnectionStatus" : result[2]}        
        