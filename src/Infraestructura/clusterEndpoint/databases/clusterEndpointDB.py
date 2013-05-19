# -*- coding: UTF8 -*-
from editionState_t import EDITION_STATE_T
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
        self.__vmServerResourceUsageData = []
        self.__vmServerResourceUsageSegments = 0
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
    
    def processVMServerResourceUsageSegment(self, segmentNumber, segmentCount, data):
        if (data != []) :
            self.__vmServerResourceUsageData += data
            self.__vmServerResourceUsageSegments += 1
            
        if (self.__vmServerResourceUsageSegments == segmentCount) :
            # Hemos recibido la secuencia completa => la procesamos
            receivedData = ClusterEndpointDBConnector.__getVMServersDictionary(self.__vmServerResourceUsageData)
            registeredIDs = self.__getKnownVMServerIDs("VirtualMachineServerStatus")
            
            # Quitar las filas que no existen
            if (registeredIDs != None) :
                for ID in registeredIDs :
                    if not (receivedData.has_key(ID)) :
                        self.__deleteVMServerStatusData(ID)
                        
            # Determinar qué hay que insertar y qué hay que modificar
            inserts = []
            for ID in receivedData.keys() :
                if (registeredIDs != None and ID in registeredIDs) :
                    self.__updateVMServerStatusData(receivedData[ID])
                else :
                    inserts.append(receivedData[ID])
                    
            # Realizar las inserciones de golpe
            if (inserts != []) :
                self.__insertVMServerStatusData(inserts)
            self.__vmServerResourceUsageData = []
            self.__vmServerResourceUsageSegments = 0
            
    def __insertVMServerStatusData(self, tupleList):
        update = "INSERT INTO VirtualMachineServerStatus VALUES {0};"\
            .format(ClusterEndpointDBConnector.__convertTuplesToSQLStr(tupleList))
        self._executeUpdate(update)
            
    def __updateVMServerStatusData(self, receivedData):
        update = "UPDATE VirtualMachineServerStatus SET hosts = {0}, ramInUse = {1}, ramSize = {2},\
            freeStorageSpace = {3}, availableStorageSpace = {4}, freeTemporarySpace = {5}, availableTemporarySpace = {6},\
            activeVCPUs = {7}, physicalCPUs = {8} WHERE serverName = '{9}';".format(receivedData[1], receivedData[2], receivedData[3],
                                                           receivedData[4], receivedData[5], receivedData[6], receivedData[7],
                                                           receivedData[8], receivedData[9], receivedData[0])
        self._executeUpdate(update)
            
    def __deleteVMServerStatusData(self, serverID):
        update = "DELETE FROM VirtualMachineServerStatus WHERE serverID = '{0}';".format(serverID)
        self._executeUpdate(update)
    
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
            # Sacar los IDs de las imágenes en edición            
            
            receivedData = ClusterEndpointDBConnector.__getActiveVMsDictionary(self.__activeVMSegmentsData[vmServerIP])
            registeredIDs = self.__getActiveVMIDs()
            
            
            # Quitar las filas que haga falta
            if (registeredIDs != None) :
                for ID in registeredIDs :                    
                    if not (receivedData.has_key(ID)) :
                        domainUID = self.__getDomainUID(ID[0], ID[1], ID[2])
                        self.__deleteActiveVM(ID)
                        self.updateEditedImageStatus(domainUID, EDITION_STATE_T.TRANSFER_TO_REPOSITORY, EDITION_STATE_T.VM_ON)
                        
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
                
    def __getKnownVMServerIDs(self, table="VirtualMachineServer"):
        """
        Devuelve los identificadores de los servidores de máquinas virtuales conocidos.
        Argumentos:
            Ninguno
        Devuelve:
            Una lista con los identificadores de los servidores de máquinas virtuales conocidos.
        """
        query = "SELECT serverName FROM {0};".format(table)
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
                osFamily, osVariant, isBaseImage, isBootable, imageID FROM Image WHERE imageID = {0}".format(imageID)
            result = self._executeQuery(query, True)
            if (result == None) : 
                query = "SELECT name, description, vanillaImageFamilyID,\
                osFamily, osVariant, isBaseImage, imageID FROM EditedImage WHERE imageID = {0}".format(imageID)
                result = self._executeQuery(query, True)
                if (result == None) :
                    return None
            d = dict()
            d["ImageName"] = str(result[0])
            d["ImageDescription"] = str(result[1])
            d["VanillaImageFamilyID"] = int(result[2])
            d["OSFamily"] = int(result[3])
            d["OSVariant"] = int(result[4])
            d["IsBaseImage"] = result[5] == 1
            d["IsBootable"] = result[6] == 1
            d["State"] = EDITION_STATE_T.NOT_EDITED
            d["ImageID"] = int(result[7])
        else :
            query = "SELECT name, description, vanillaImageFamilyID,\
                osFamily, osVariant, ownerID, imageID, state FROM EditedImage WHERE temporaryID = '{0}'".format(imageID)
            result = self._executeQuery(query, True)
            d = dict()
            d["ImageName"] = str(result[0])
            d["ImageDescription"] = str(result[1])
            d["VanillaImageFamilyID"] = int(result[2])
            d["OSFamily"] = int(result[3])
            d["OSVariant"] = int(result[4])
            d["IsBaseImage"] = False
            d["IsBootable"] = False
            d["State"] = int(result[7])
            d["OwnerID"] = int(result[5])
            d["ImageID"] = int(result[6])
        
        return d       
        
    def getBootableImagesData(self, imageIDs):
        query = "SELECT imageID, name, description, vanillaImageFamilyID,\
                osFamily, osVariant FROM Image WHERE isBootable = 0"
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
            
    def getEditedImageIDs(self, userID=None):
        if (userID != None) :
            query = "SELECT temporaryID FROM EditedImage WHERE ownerID = {0};".format(userID)
        else :
            query = "SELECT temporaryID FROM EditedImage;"
        result = self._executeQuery(query, False)
        rows = []
        if (result != None) :
            for row in result :
                rows.append(str(row))
        return rows
    
    def getVanillaImageFamilyID(self, imageID):
        if (isinstance(imageID, int)) :
            query = "SELECT vanillaImageFamilyID FROM Image WHERE imageID = {0}".format(imageID)
            result = self._executeQuery(query, True)
            if (result == None) :
                query = "SELECT vanillaImageFamilyID FROM EditedImage WHERE imageID = {0}".format(imageID)
                result = self._executeQuery(query, True)
            return result
        else :
            query = "SELECT vanillaImageFamilyID FROM EditedImage WHERE temporaryID = '{0}'".format(imageID)
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
        
    def getVirtualMachineServerStatus(self, serverName):
        query = "SELECT hosts, ramInUse, ramSize, freeStorageSpace, availableStorageSpace, \
            freeTemporarySpace, availableTemporarySpace, activeVCPUs, physicalCPUs\
            FROM VirtualMachineServerStatus WHERE serverName = '{0}';".format(serverName)
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
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
            return d  
   
    def getOSTypes(self):
        query = "SELECT familyID, familyName FROM OSFamily;"
        results = self._executeQuery(query, False)
        if (results == None) :
            return []
        retrievedData = []
        for row in results :
            d = dict()
            d["FamilyID"] = row[0]
            d["FamilyName"] = row[1]
            retrievedData.append(d)
        return retrievedData
        
    def getOSTypeVariants(self,familyID):
        query = "SELECT variantID, variantName FROM OSVariant WHERE familyID = '{0}';".format(familyID)
        results = self._executeQuery(query, False)
        if (results == None) :
            return []
        retrievedData = []
        for row in results :
            d = dict()
            d["VariantID"] = row[0]
            d["VariantName"] = row[1]
            retrievedData.append(d)
        return retrievedData    
    
    def addNewImage(self, temporaryID, baseImageID, ownerID, imageName, imageDescription):
        # Sacar los datos de la imagen base
        baseImageData = self.getImageData(baseImageID)
        update = "INSERT INTO EditedImage VALUES('{0}', {1}, {2}, '{3}', '{4}', {5}, {6}, {7}, {8});"\
            .format(temporaryID, baseImageData["VanillaImageFamilyID"], -1, imageName, imageDescription,
                    baseImageData["OSFamily"], baseImageData["OSVariant"], ownerID, EDITION_STATE_T.DEPLOYMENT)
        self._executeUpdate(update)
        
    def editImage(self, commandID, imageID, ownerID):
        query = "SELECT * from EditedImage WHERE imageID = {0};".format(imageID)
        if (self._executeQuery(query, True) != None) :
            update = "UPDATE EditedImage SET temporaryID = '{0}', state = {2} WHERE imageID = {1};".format(commandID, imageID, EDITION_STATE_T.DEPLOYMENT)
            self._executeUpdate(update)
        else :
            imageData = self.getImageData(imageID)
            update = "DELETE FROM Image WHERE imageID = {0};".format(imageID)
            self._executeUpdate(update)
            update = "INSERT INTO EditedImage VALUES('{0}', {1}, {2}, '{3}', '{4}', {5}, {6}, {7}, {8});"\
                .format(commandID, imageData["VanillaImageFamilyID"], imageID, imageData["ImageName"], imageData["ImageDescription"],
                        imageData["OSFamily"], imageData["OSVariant"], ownerID, EDITION_STATE_T.DEPLOYMENT)
            self._executeUpdate(update)
        
    def deleteEditedImage(self, temporaryID):
        update = "DELETE FROM EditedImage WHERE temporaryID = '{0}';".format(temporaryID)
        self._executeUpdate(update)
        
    def updateEditedImageStatus(self, temporaryID, newStatus, expectedStatus=None):
        if (expectedStatus != None) : 
            query = "SELECT state FROM EditedImage WHERE temporaryID = '{0}';".format(temporaryID)
            if (self._executeQuery(query, True) != expectedStatus) :
                return
        update = "UPDATE EditedImage SET state = {1} WHERE temporaryID = '{0}';".format(temporaryID, newStatus)
        self._executeUpdate(update)
        
    def registerImageID(self, temporaryID, imageID):
        update = "UPDATE EditedImage SET imageID = {1}, state = {2} WHERE temporaryID = '{0}';".format(temporaryID, imageID, EDITION_STATE_T.CHANGES_NOT_APPLIED)
        self._executeUpdate(update)
        
    def makeBootable(self, imageID):
        update = "UPDATE Image SET isBootable = 1 WHERE imageID = {0};".format(imageID)
        self._executeUpdate(update)
        
    def __getDomainUID(self, serverName, ownerID, imageID):
        query = "SELECT domainUID FROM ActiveVirtualMachines WHERE serverName = '{0}' AND ownerID = {1} AND imageID = {2};"\
            .format(serverName, ownerID, imageID)
        return self._executeQuery(query, True)
        
    def unregisterDomain(self, domainUID):
        update = "DELETE FROM ActiveVirtualMachines WHERE domainUID = '{0}';".format(domainUID)
        self._executeUpdate(update)