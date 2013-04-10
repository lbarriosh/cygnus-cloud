# -*- coding: UTF8 -*-
'''
Escritor de la base de datos de estado

@author: Luis Barrios Hernández
@version: 3.5
'''

from database.utils.connector import BasicDatabaseConnector

class SystemStatusDatabaseWriter(BasicDatabaseConnector):
    """
    Estos objetos actualizan la base de estado con la información que envía el servidor de cluster
    """
    def __init__(self, sqlUser, sqlPassword, databaseName):
        """
        Inicializa el estado del escritor
        Argumentos:
            sqlUser: usuario SQL a utilizaqr
            sqlPassword: contraseña de ese usuario
            databaseName: nombre de la base de datos de estado
        """
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPassword, databaseName)
        self.__vmServerSegmentsData = []
        self.__vmServerSegments = 0
        self.__imageDistributionSegmentsData = []
        self.__imageDistributionSegments = 0
        self.__activeVMSegmentsData = dict()
        self.__activeVMSegments = dict()
        
        
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
            receivedData = SystemStatusDatabaseWriter.__getVMServersDictionary(self.__vmServerSegmentsData)
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
                command = "INSERT INTO VirtualMachineDistribution VALUES " + SystemStatusDatabaseWriter.__convertSegmentsToSQLTuples(self.__imageDistributionSegmentsData)
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
            receivedData = SystemStatusDatabaseWriter.__getActiveVMsDictionary(self.__activeVMSegmentsData[vmServerIP])
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
        for t in output :
            result.add(t[0])
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
            .format(SystemStatusDatabaseWriter.__convertTuplesToSQLStr(tupleList))
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
            .format(SystemStatusDatabaseWriter.__convertTuplesToSQLStr(data, [vmServerIP]))
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
        return result[0]
                        
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