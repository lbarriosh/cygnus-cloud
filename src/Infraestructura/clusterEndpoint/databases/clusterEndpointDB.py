# -*- coding: UTF8 -*-
'''
Lector de la base de datos de estado

@author: Luis Barrios Hernández
@version: 2.5
'''

from ccutils.databases.connector import BasicDatabaseConnector

class ClusterEndpointDBConnector(BasicDatabaseConnector):
    """
    Inicializa el estado del lector
    Argumentos:
        sqlUser: usuario SQL a utilizaqr
        sqlPassword: contraseña de ese usuario
        databaseName: nombre de la base de datos de estado
    """
    def __init__(self, sqlUser, sqlPassword, databaseName):
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPassword, databaseName)
        self.__vmServerSegmentsData = []
        self.__vmServerSegments = 0
        self.__imageDistributionSegmentsData = []
        self.__imageDistributionSegments = 0
        self.__activeVMSegmentsData = dict()
        self.__activeVMSegments = dict()
                  
    def getVMServersData(self):
        """
        Devuelve los datos básicos de todos los servidores de máquinas virtuales
        Argumentos:
            Ninguno
        Returns: una lista de diccionarios, cada uno de los cuales contiene los datos
        de un servidor de máquinas virtuales
        """
        command = "SELECT * FROM VirtualMachineServer;"
        results = self._executeQuery(command, False)
        if (results == None) :
            return []
        retrievedData = []
        for row in results :
            d = dict()
            d["VMServerName"] = row[0]
            d["VMServerStatus"] = row[1]
            d["VMServerIP"] = row[2]
            d["VMServerListenningPort"] = int(row[3])
            d["IsVanillaServer"] = int(row[4]) == 1
            retrievedData.append(d)
        return retrievedData
    
    def getVMDistributionData(self):
        """
        Devuelve la distribución de todas las máquinas virtuales
        Argumentos:
            Ninguno
        Devuelve: 
            una lista de diccionarios. Cada uno contiene una ubicación de una
            imagen.
        """
        command = "SELECT * FROM VirtualMachineDistribution;"
        results = self._executeQuery(command, False)
        if (results == None) :
            return []
        retrievedData = []
        for row in results :
            d = dict()
            d["VMServerName"] = row[0]
            d["ImageID"] = int(row[1])
            d["CopyStatus"] = row[2]
            retrievedData.append(d)
        return retrievedData 
    
    def getActiveVMsData(self, ownerID):
        """
        Devuelve los datos de las máquinas virtuales activas
        Argumentos:
            ownerID: identificador del propietario de las máquinas. Si es None, se devolverán
            los datos de todas las máquinas virtuales.
        Devuelve: 
            una lista de diccionarios. Cada uno contiene los datos de una máquina
        """
        if (ownerID == None) :
            command = "SELECT * FROM ActiveVirtualMachines;"
        else :
            command = "SELECT * FROM ActiveVirtualMachines WHERE ownerID = {0};".format(ownerID)
            
        results = self._executeQuery(command, False)
        if (results == None) :
            return []
        retrievedData = []
        for row in results :
            d = dict()
            d["VMServerName"] = row[0]
            d["DomainUID"] = row[1]
            d["UserID"] = row[2]
            d["VMID"] = int(row[3])            
            d["VMName"] = row[4]
            d["VNCPort"] = int(row[5])
            d["VNCPassword"] = row[6]
            retrievedData.append(d)
        return retrievedData 
    
    def processVMServerSegment(self, segmentNumber, segmentCount, data):
        """
        Procesa un segmento con datos de los servidores de máquinas virtuales
        Argumentos:
            segmentNumber: posición del segmento en la secuencia
            segmentCount: número de segmentos de la secuencia
            data: los datos del segmento
        Devuelve:
            Nada
        """
        # Guardamos los datos del segmento (si los hay)
        if (data != []) :
            self.__vmServerSegmentsData += data
            self.__vmServerSegments += 1
            
        if (self.__vmServerSegments == segmentCount) :
            # Hemos recibido la secuencia completa => la procesamos
            receivedData = ClusterEndpointDBConnector.__getVMServersDictionary(self.__vmServerSegmentsData)
            registeredIDs = self.__getKnownVMServerIDs()
            
            # Quitar las filas que no existen
            if (registeredIDs != None) :
                for ID in registeredIDs :
                    if not (receivedData.has_key(ID)) :
                        self.__deleteVMServer(ID)
                        
            # Determinar qué hay que insertar y qué hay que modificar
            inserts = []
            for ID in receivedData.keys() :
                if (registeredIDs != None and ID in registeredIDs) :
                    self.__updateVMServerData(receivedData[ID])
                else :
                    inserts.append(receivedData[ID])
                    
            # Realizar las inserciones de golpe
            if (inserts != []) :
                self.__insertVMServers(inserts)
            self.__vmServerSegmentsData = [] 
            self.__vmServerSegments = 0
            
    def processVMDistributionSegment(self, segmentNumber, segmentCount, data):
        """
        Procesa un segmento con datos de la distribución de las imágenes
        Argumentos:
            segmentNumber: posición del segmento en la secuencia
            segmentCount: número de segmentos de la secuencia
            data: los datos del segmento
        Devuelve:
            Nada
        """
        if (data != []) :
            self.__imageDistributionSegmentsData.append(data)
            self.__imageDistributionSegments += 1
        if (self.__imageDistributionSegments == segmentCount) :            
            # Borrar la tabla y volver a construirla
            command = "DELETE FROM VirtualMachineDistribution;"
            self._executeUpdate(command)
            if (self.__imageDistributionSegmentsData != []) :
                command = "INSERT INTO VirtualMachineDistribution VALUES " + ClusterEndpointDBConnector.__convertSegmentsToSQLTuples(self.__imageDistributionSegmentsData)
                self.__imageDistributionSegmentsData = []   
                self.__imageDistributionSegments = 0         
                self._executeUpdate(command)
    
    def processActiveVMSegment(self, segmentNumber, segmentCount, vmServerIP, data):
        """
        Procesa un segmento con datos de las máquinas virtuales activas
        Argumentos:
            segmentNumber: posición del segmento en la secuencia
            segmentCount: número de segmentos de la secuencia
            data: los datos del segmento
        Devuelve:
            Nada
        """
        if (not self.__activeVMSegmentsData.has_key(vmServerIP)) :
            self.__activeVMSegmentsData[vmServerIP] = []
            self.__activeVMSegments[vmServerIP] = 0
        if (data != []) :
            self.__activeVMSegmentsData[vmServerIP] += data
            self.__activeVMSegments[vmServerIP] += 1
        if (self.__activeVMSegments[vmServerIP] == segmentCount) :
            receivedData = ClusterEndpointDBConnector.__getActiveVMsDictionary(self.__activeVMSegmentsData[vmServerIP])
            registeredIDs = self.__getActiveVMIDs()
            
            # Quitar las filas que haga falta
            if (registeredIDs != None) :
                for ID in registeredIDs :
                    if not (receivedData.has_key(ID)) :
                        self.__deleteActiveVM(ID)
                        
            # Realizar las actualizaciones y preparar las inserciones
            inserts = []
            for ID in receivedData.keys() :
                if (registeredIDs != None and not (ID in registeredIDs)) :
                    inserts.append(receivedData[ID])
                    
            # Realizar las inserciones
            if (inserts != []) :
                self.__insertActiveVMData(self.__getVMServerName(vmServerIP), inserts)
            self.__activeVMSegmentsData[vmServerIP] = []
            self.__activeVMSegments[vmServerIP] = 0
        
    @staticmethod    
    def __getVMServersDictionary(segmentList):
        """
        Genera un diccionario a partir de  una lista de tuplas con datos de los servidores de máquinas virtuales
        Argumentos:
            segmentList: la lista de tuplas que queremos convertir a diccionario
        Devuelve:
            Un diccionario de la forma <ID del servidor, tupla)
        """
        result = {}
        for segment in segmentList :
            result[segment[0]] = segment
        return result
    
    @staticmethod
    def __getActiveVMsDictionary(segmentList):
        """
        Genera un diccionario a partir de  una lista de tuplas con datos de las máquinas virtuales
        activas.
        Argumentos:
            segmentList: la lista de tuplas que queremos convertir a diccionario
        Devuelve:
            Un diccionario de la forma <ID de la máquina (usuario, imagen, servidor), tupla)
        """
        result = {}
        for segment in segmentList :
            result[(segment[0], segment[1], segment[2])] = segment
        return result
                
    def __getKnownVMServerIDs(self):
        """
        Devuelve los identificadores de los servidores de máquinas virtuales conocidos.
        Argumentos:
            Ninguno
        Devuelve:
            Una lista con los identificadores de los servidores de máquinas virtuales conocidos.
        """
        query = "SELECT serverName FROM VirtualMachineServer;";
        result = set()
        output = self._executeQuery(query, False)
        if (output == None) :
            return None
        for t in output :
            result.add(t)
        return result
            
    def __insertVMServers(self, tupleList):
        """
        Inserta las tuplas con datos de los servidores de máquinas virtuales de una lista en la base de datos.
        Argumentos:
            tupleList: la lista de tuplas con los datos a insertar
        Devuelve:
            Nada
        """
        update = "INSERT INTO VirtualMachineServer VALUES {0};"\
            .format(ClusterEndpointDBConnector.__convertTuplesToSQLStr(tupleList))
        self._executeUpdate(update)
        
    def __updateVMServerData(self, data):
        """
        Actualiza la información de un servidor de máquinas virtuales
        Argumentos: 
            data: tupla con la nueva información del servidor de máquinas virtuales
        Devuelve:
            Nada            
        """        
        update = "UPDATE VirtualMachineServer SET serverStatus='{1}', serverIP='{2}', serverPort={3},\
            isVanillaServer = {4} WHERE serverName='{0}'".format(data[0], data[1], data[2], data[3], data[4])
        self._executeUpdate(update)
        
    def __deleteVMServer(self, serverID):
        """
        Borra un servidor de máquinas virtuales de la base de datos de estado
        Argumentos:
            serverID: el identificador del servidor a borrar
        Devuelve:
            Nada
        """
        # Importante: ON DELETE CASCADE NO funciona con las tablas alojadas en memoria, por lo que
        # lo tenemos que implementar a mano.
        update = "DELETE FROM ActiveVirtualMachines WHERE serverName = '{0}';".format(serverID)
        self._executeUpdate(update)
        update = "DELETE FROM VirtualMachineServer WHERE serverName = '{0}'".format(serverID)
        self._executeUpdate(update)        
            
    def __getActiveVMIDs(self):
        """
        Devuelve los identificadores únicos de las máquinas virtuales activas (en su forma larga)
        Argumentos:
            Ninguno
        Returns:
            una lista con los identificadores únicos de las máquinas virtuales activas
        """
        query = "SELECT serverName, ownerID, imageID FROM ActiveVirtualMachines;"
        results = self._executeQuery(query)
        if (results == None) :
            return set()
        output = set()
        for row in results :
            output.add((row[0], row[1], row[2]))
        return output
    
    def __insertActiveVMData(self, vmServerIP, data):
        """
        Inserta los datos de las máquinas alojadas en cierto servidor en la base de datos de estado
        Argumentos:
            vmServerIP: la IP del servidor de máquinas virtuales que aloja las máquinas
            data: una lista con la información de esas máquinas
        Devuelve:
            Nada
        """
        update = "INSERT INTO ActiveVirtualMachines VALUES {0};"\
            .format(ClusterEndpointDBConnector.__convertTuplesToSQLStr(data, [vmServerIP]))
        self._executeUpdate(update)
        
    def __deleteActiveVM(self, machineID):
        """
        Borra los datos de una máquina virtual activa
        Argumentos:
            machineID: el identificador único de la máuqina virtual activa
        Devuelve:
            Nada
        """
        update = "DELETE FROM ActiveVirtualMachines WHERE serverName='{0}' AND ownerID={1} AND imageID={2};"\
            .format(machineID[0], machineID[1], machineID[2])
        self._executeUpdate(update)
            
    def __getVMServerName(self, serverIP):
        """
        Devuelve el nombre del servidor de máquinas virtuales asociado a una IP
        Argumentos:
            serverIP: la IP del servidord de máquinas virtuales
        Devuelve:
            el nombre del servidor de máquinas virtuales asociado a esa IP
        """
        query = "SELECT serverName FROM VirtualMachineServer WHERE serverIP = '" + serverIP + "';"
        result = self._executeQuery(query, True)
        return str(result)
                        
    @staticmethod
    def __convertTuplesToSQLStr(tupleList, dataToAdd = []):
        """
        Convierte una lista de tuplas en un string SQL
        Argumentos:
            tupleList: lista de tuplas a convertir
            dataToAdd: lista con los datos a añadir al final de cada tupla
        Devuelve:
            Un string SQL con la información de los argumentos en forma de lista de tuplas
        """
        isFirstSegment = True
        command = ""
        for segmentTuple in tupleList :
            if (isFirstSegment) :
                isFirstSegment = False
            else :
                command += ", "
            segmentTuple_list = dataToAdd + list(segmentTuple)
            command += str(tuple(segmentTuple_list))
        return command    
    
    @staticmethod
    def __convertSegmentsToSQLTuples(segmentList):
        """
        Convierte una lista de segmentos en un string SQL
        Argumentos:
            segmentList: lista de segmentos
            dataToAdd: lista con los datos a añadir al final de cada tupla
        Devuelve:
            Un string SQL con la información de los argumentos en forma de lista de tuplas
        """
        isFirstSegment = True
        command = ""
        for segment in segmentList :
            for segmentTuple in segment :
                if (isFirstSegment) :
                    isFirstSegment = False
                else :
                    command += ", "
                command += str(segmentTuple)
        command += ";"
        return command    
    
    def getImageData(self, imageID):
        
        if (isinstance(imageID, int)) :
            query = "SELECT name, description, vanillaImageFamilyID,\
                osFamily, osVariant, isBaseImage, bootable, edited,\
                ownerID FROM Image WHERE imageID = {0}".format(imageID)
            result = self._executeQuery(query, True)
            if (result == None) : return None
            d = dict()
            d["ImageName"] = str(result[0])
            d["ImageDescription"] = str(result[1])
            d["AssignedToSubject"] = True
            d["VanillaImageFamilyID"] = result[2]
            d["OSFamily"] = result[3]
            d["OSVariant"] = result[4]
            d["IsBaseImage"] = result[5] == 1
            d["IsBootable"] = result[6] == 1
            d["IsEdited"] = result[7] == 1
            d["OwnerID"] = result[8]
        else :
            query = "SELECT name, description, vanillaImageFamilyID,\
                osFamily, osVariant, ownerID FROM NewImage WHERE temporaryID = '{0}'".format(imageID)
            result = self._executeQuery(query, True)
            d = dict()
            d["ImageName"] = str(result[0])
            d["ImageDescription"] = str(result[1])
            d["AssignedToSubject"] = False
            d["VanillaImageFamilyID"] = result[2]
            d["OSFamily"] = result[3]
            d["OSVariant"] = result[4]
            d["IsBaseImage"] = False
            d["IsBootable"] = False
            d["IsEdited"] = True
            d["OwnerID"] = result[5]
        
        return d       
        
    def getBootableImagesData(self, imageIDs):
        query = "SELECT imageID, name, description, vanillaImageFamilyID,\
                osFamily, osVariant FROM Image WHERE bootable = 1"
        if (imageIDs != []) :
            query += " AND ("
            i = 0
            for imageID in imageIDs :
                query += "imageID = {0} ".format(imageID)
                if (i != len(imageIDs) - 1) :
                    query += " OR "
                i += 1
            query += ");"
        result = self._executeQuery(query, False)        
        if (result == None) :
            return []
        else :
            rows = []
            for row in result :
                rows.append({"ImageID": row[0], "ImageName" : str(row[1]), "ImageDescription" : str(row[2]),
                             "VanillaImageFamilyID" : row[3], "OSFamily" : row[4], "OSVariant" : row[5]})
        return rows
    
    def getBaseImagesData(self):
        query = "SELECT imageID, name, description, vanillaImageFamilyID,\
                osFamily, osVariant FROM Image WHERE isBaseImage = 1;"
        result = self._executeQuery(query, False)
        if (result == None) :
            return []
        else :
            rows = 0
            rows = []
            for row in result :
                rows.append({"ImageID": row[0], "ImageName" : str(row[1]), "ImageDescription" : str(row[2]),
                             "VanillaImageFamilyID" : row[3], "OSFamily" : row[4], "OSVariant" : row[5]})
            return rows
        
    def getEditedImageIDs(self, userID):
        query = "SELECT imageID FROM Image WHERE edited = 1 AND ownerID = {0};".format(userID)
        result = self._executeQuery(query, False)
        rows = []
        if (result != None) :
            for row in result :
                rows.append(row)
        return rows
    
    def getNewImageIDs(self, userID):
        query = "SELECT temporaryID FROM NewImage WHERE ownerID = {0};".format(userID)
        result = self._executeQuery(query, False)
        rows = []
        if (result != None) :
            for row in result :
                rows.append(str(row))
        return rows
    
    def getVanillaImageFamilyID(self, imageID):
        if (isinstance(imageID, int)) :
            query = "SELECT vanillaImageFamilyID FROM Image WHERE imageID = {0}".format(imageID)
        else :
            query = "SELECT vanillaImageFamilyID FROM NewImage WHERE temporaryID = '{0}'".format(imageID)
        return self._executeQuery(query, True)
    
    def getVanillaImageFamilyData(self, vanillaImageFamilyID):
        query = "SELECT familyName, ramSize, vCPUs, osDiskSize, dataDiskSize FROM VanillaImageFamily WHERE familyID = {0}".format(vanillaImageFamilyID)
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            return {"Name" : str(result[0]), "RAMSize" : result[1], "VCPUs": result[2], "OSDiskSize" : result[3], "DataDiskSize" : result[4]}
        
    def getMaxVanillaImageFamilyData(self):
        query = "SELECT MAX(ramSize), MAX(vCPUs), MAX(osDiskSize), MAX(dataDiskSize) FROM VanillaImageFamily;"
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            return {"RAMSize" : result[0], "VCPUs": result[1], "OSDiskSize" : result[2], "DataDiskSize" : result[3]}
        
    def updateImageRepositoryStatus(self, freeDiskSpace, availableDiskSpace, status) :
        query = "SELECT * FROM ImageRepositoryStatus;"
        result = self._executeQuery(query, True)
        if (result == None) :
            command = "INSERT INTO ImageRepositoryStatus VALUES (1, {0}, {1}, '{2}');".format(freeDiskSpace, availableDiskSpace, status)
        else :
            command = "UPDATE ImageRepositoryStatus SET freeDiskSpace = {0}, availableDiskSpace = {1}, repositoryStatus = '{2}';"\
                .format(freeDiskSpace, availableDiskSpace, status)
        self._executeUpdate(command)
        
    def getImageRepositoryStatus(self):
        query = "SELECT freeDiskSpace, availableDiskSpace, repositoryStatus FROM ImageRepositoryStatus;"
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            d = dict()
            d["FreeDiskSpace"] = result[0]
            d["AvailableDiskSpace"] = result[1]
            d["RepositoryStatus"] = str(result[2])
            return d