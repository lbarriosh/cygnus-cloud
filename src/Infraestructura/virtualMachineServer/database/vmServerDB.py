# -*- coding: UTF8 -*-
from ccutils.databases.connector import BasicDBConnector
from ccutils.enums import enum

TRANSFER_T = enum("CREATE_IMAGE", "EDIT_IMAGE", "DEPLOY_IMAGE", "STORE_IMAGE", "CANCEL_EDITION") 

class VMServerDBConnector(BasicDBConnector):
    '''
        Esta clase permite gestionar las diferentes características de las imágenes 
         accesibles en el servidor de máquinas virtuales actual.
    '''

    def __init__(self, sqlUser, sqlPass, databaseName):
        '''
            Constructora de la clase
        '''
        BasicDBConnector.__init__(self, sqlUser, sqlPass, databaseName)
        self.generateMACsAndUUIDs()
        self.generateVNCPorts()
        
    def getImageIDs(self):
        '''
             Devuelve una lista con todos los identificadores de imágenes que se 
              encuentran registradas en el servidor de máquinas virtuales.
        '''      
        sql = "SELECT ImageID FROM VirtualMachine" 
        results = self._executeQuery(sql, False)
        imageIds = []
        for r in results:
            imageIds.append(r)
        return imageIds
    
    def getDataImagePath(self, imageID):
        '''
            Devuelve la ruta donde se encuentra físicamente la imagen cuyo identificador 
             de imagen se pasa como argumento.
        '''
        sql = "SELECT dataImagePath FROM VirtualMachine WHERE ImageID = {0};".format(imageID)   
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result
    
    def getOSImagePath(self, imageID):
        '''
            Devuelve la ruta donde se encuentra físicamente la imagen del SO cuyo identificador 
             de imagen se pasa como argumento.
        '''
        sql = "SELECT osImagePath FROM VirtualMachine WHERE ImageID = {0};".format(imageID)
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result
    
    def getDefinitionFilePath(self, imageID):
        '''
            Devuelve la ruta donde se encuentra el fichero de configuración asociado a 
             la imagen cuyo identificador se pasa como argumento
        '''
        sql = "SELECT definitionFilePath FROM VirtualMachine WHERE ImageID = {0};".format(imageID)   
        result = self._executeQuery(sql)
        if (result == None) : 
            return None
        return result[0]
        
    def createImage(self, imageID, osImagePath, dataImagePath, definitionFilePath, bootable):
        '''
            Permite registrar en la base de datos una nueva imagen de máquina virtual. 
        '''
        if (bootable) : bootableFlag = 1
        else : bootableFlag = 0
        
        update = "INSERT INTO VirtualMachine VALUES ({0}, '{1}', '{2}', '{3}', {4})"\
            .format(imageID, osImagePath, dataImagePath, definitionFilePath, bootableFlag)          
        self._executeUpdate(update)  
        
    def getBootableFlag(self, imageID):
        query = "SELECT bootable FROM VirtualMachine WHERE ImageID = {0};".format(imageID)
        flag = self._executeQuery(query, True)
        return flag == 1
    
    def deleteImage(self, imageID):
        sql = "DELETE FROM VirtualMachine WHERE ImageID = {0};".format(imageID)
        self._executeUpdate(sql) 
    
    def generateMACsAndUUIDs(self): 
        '''
            Función encargada de crear la tabla inicial de pares (UUID,MAC) libres
        '''
        sql = "DROP TABLE IF EXISTS FreeMACs"         
        self._executeUpdate(sql)  
        sql = "CREATE TABLE IF NOT EXISTS FreeMACs(UUID VARCHAR(40) ,MAC VARCHAR(20),PRIMARY KEY(UUID,MAC)) ENGINE=MEMORY;"
        self._executeUpdate(sql)
        v = 0
        while v < 256 :
            x = str(hex(v))[2:].upper()
            if v < 16:
                x = '0' + x
            sql = "INSERT INTO FreeMACs VALUES (UUID(),'" + '2C:00:00:00:00:' + x + "');"
            self._executeUpdate(sql)
            v = v + 1
            
        
    def generateVNCPorts(self): 
        '''
            Función encargada de crear la tabla inicial de pares (UUID,MAC) libres
        '''
        sql = "DROP TABLE IF EXISTS FreeVNCPorts;" 
        self._executeUpdate(sql)  
        sql = "CREATE TABLE IF NOT EXISTS FreeVNCPorts(VNCPort INTEGER PRIMARY KEY) ENGINE=MEMORY;"
        self._executeUpdate(sql)
        p = 15000
        v = 0
        while v < 256 :
            sql = "INSERT INTO FreeVNCPorts VALUES ('" + str(p) + "');"
            self._executeUpdate(sql)
            p = p + 2
            v = v + 1
        
    def extractFreeMACAndUUID(self):
        '''
            Función que devuelve la primera ocurrencia de la tabla de macs libres y
             la elimina de la tabla
        '''
        sql = "SELECT * FROM FreeMACs"
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None        
        sql = "DELETE FROM FreeMACs WHERE UUID = '" + result[0] + "' AND MAC ='" + result[1] + "'"
        self._executeUpdate(sql)
        return (result[0], result[1])
    
    def freeMACAndUUID(self, UUID, MAC):
        '''
            Añade un nuevo par del tipo UUID , MAC a la tabla freeMAC
        '''
        sql = "INSERT INTO FreeMACs VALUES ('" + UUID + "','" + MAC + "')"
        self._executeUpdate(sql)
        
    def extractFreeVNCPort(self):
        '''
            Función que devuelve la primera ocurrencia de la tabla de macs libres y
             la elimina de la tabla
        '''
        sql = "SELECT * FROM FreeVNCPorts"
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        sql = "DELETE FROM FreeVNCPorts WHERE VNCPort = '" + str(result) + "'"
        self._executeUpdate(sql)
        return result
    
    def freeVNCPort(self, VNCPort):
        '''
            Añade un nuevo par del tipo UUID , MAC a la tabla freeMAC
        '''
        sql = "INSERT INTO FreeVNCPorts VALUES ('" + str(VNCPort) + "')"
        self._executeUpdate(sql)      
    
    def getDomainDataImagePath(self, domainName):
        '''
            Devuelve la ruta asociada a la copia de la imagen de la máquina virtual que se encuentra 
             en ejecución en el puertoVNC pasado como argumento.
        '''
        sql = "SELECT dataImagePath FROM ActualVM  WHERE domainName = '{0}';".format(domainName)        
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result
    
    def getDomainMACAddress(self, domainName):
        '''
            Devuelve la dirección MAC del cliente VNC cuyo puerto se pasa como argumento.
        '''
        sql = "SELECT macAddress FROM ActualVM WHERE domainName = '" + str(domainName) + "'" 
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result
    
    def getDomainUUID(self, domainName):
        '''
            Devuelve la uuid del cliente VNC cuyo puerto se pasa como argumento.
        '''
        sql = "SELECT uuid FROM ActualVM WHERE domainName = '" + str(domainName) + "'" 
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result
    
    def getDomainVNCPassword(self, domainName): 
        '''
            Devuelve la contraseña que se ha dado al puerto VNC que se le pasa como argumento.
        '''         
        sql = "SELECT VNCPass FROM ActualVM WHERE domainName = '" + str(domainName) + "'" 
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result

    def getWebsockifyDaemonPID(self, domainName): 
        '''
            Devuelve la contraseña que se ha dado el dominio que se le pasa como argumento.
        ''' 
        sql = "SELECT webSockifyPID FROM ActualVM WHERE domainName = '" + str(domainName) + "'" 
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result
    
    
    def getDomainOSImagePath(self, domainName): 
        '''
            Devuelve la contraseña que se ha dado al dominio que se le pasa como argumento.
        '''         
        sql = "SELECT osImagePath FROM ActualVM WHERE domainName = '" + str(domainName) + "'" 
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result
    
    def getDomainImageID(self, domainName):
        '''
            Devuelve el identificador de la máquina virtual que se encuentra en ejecución en el 
            dominio pasado como argumento.
        '''
        sql = "SELECT ImageID FROM ActualVM WHERE domainName = '" + str(domainName) + "'" 
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result         
    
    def getDomainNameFromVNCPort(self, vncPort): 
        '''
            Devuelve la contraseña que se ha dado al puerto VNC que se le pasa como argumento.
        '''        
        sql = "SELECT domainName FROM ActualVM WHERE VNCPort = '" + str(vncPort) + "'" 
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return result
    
    def registerVMResources(self, domainName, ImageID, vncPort, vncPassword, userId, webSockifyPID, osImagePath, dataImagePath, mac, uuid):
        '''
            Permite dar de alta una nueva máquina virtual en ejecución cuyas características se pasan
             como argumentos.
        '''
        sql = "INSERT INTO ActualVM VALUES('{0}', {1}, {2}, '{3}', {4}, {5}, '{6}', '{7}', '{8}', '{9}')" \
            .format(domainName, ImageID, vncPort, vncPassword, userId, webSockifyPID,
                    osImagePath, dataImagePath, mac, uuid);
        self._executeUpdate(sql)        
        return vncPort 
    
    def unregisterDomainResources(self, domainName):
        '''
            Da de baja en la base de datos el puerto VNC que se le pasa como argumento 
             y con él, todas las características asociadas al mismo.
        ''' 
        update = "DELETE FROM ActualVM WHERE domainName = '" + str(domainName) + "'"
        self._executeUpdate(update)    
    
    def getDomainOwnerID(self, domainName):
        '''
            Devuelve el identificador del usuario asociado a la mv que se encuentra en ejecución en el 
            dominio pasado como argumento.
        '''
        sql = "SELECT userId FROM ActualVM WHERE domainName = '" + str(domainName) + "'" 
        result = self._executeQuery(sql, True)
        if (result == None) : 
            return None
        return int(result)
    
    def getDomainsConnectionData(self):
        '''
        Devuelve una lista con los datos de conexión a las máquinas vituales activas
        Argumentos:
            Ninguno
        Devuelve:
            Lista de diccionarios con los datos de conexión a las máquinas virtuales
        '''
        query = "SELECT ActiveDomainUIDs.commandID, ActualVM.userId, ActualVM.ImageID, ActualVM.domainName, ActualVM.VNCPort, ActualVM.VNCPass\
            FROM ActualVM, ActiveDomainUIDs WHERE ActualVM.domainName = ActiveDomainUIDs.domainName;"
        results = self._executeQuery(query, False)
        if (results == None) :
            return []
        else :
            ac = []
            for row in results:
                ac.append({"DomainID" : row[0], "UserID" : int(row[1]), "ImageID" : int(row[2]), "VMName": row[3], "VNCPort" : int(row[4]), "VNCPass" : row[5]})
            return ac
        
    def addVMBootCommand(self, domainName, commandID):
        update = "INSERT INTO ActiveDomainUIDs VALUES ('{0}', '{1}');".format(domainName, commandID)
        self._executeUpdate(update)
        
    def getVMBootCommand(self, domainName):
        query = "SELECT commandID FROM ActiveDomainUIDs WHERE domainName = '" + domainName + "';"
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            return result
        
    def getDomainNameFromVMBootCommand(self, commandID):
        query = "SELECT domainName FROM ActiveDomainUIDs WHERE commandID = '{0}';".format(commandID)
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        else :
            return result
    
    def __getAssignedResources(self):
        query = "SELECT macAddress, VNCPort FROM ActualVM;"
        result = self._executeQuery(query, False)
        assignedMACs, assignedVNCPorts = ([], [])
        if (result != None) :
            for row in result :
                assignedMACs.append(row[0])
                assignedVNCPorts.append(int(row[1]))
                assignedVNCPorts.append(int(row[1]) + 1)
        return (assignedMACs, assignedVNCPorts)      
    
    def __allocateMACAddressAndUUID(self, macAddr):
        command = "DELETE FROM FreeMACs WHERE MAC ='{0}';".format(macAddr)    
        self._executeUpdate(command)      
        
    def __allocatePort(self, port):
        command = "DELETE FROM FreeVNCPorts WHERE VNCPort = {0};".format(port)
        self._executeUpdate(command)
    
    def __allocateAssignedResources(self):
        assignedMACs, assignedVNCPorts = self.__getAssignedResources()
        for macAddress in assignedMACs :
            self.__allocateMACAddressAndUUID(macAddress)
        for port in assignedVNCPorts :
            self.__allocatePort(port)
            
    def getActiveDomainUIDs(self):
        """
        Devuelve los identificadores únicos de las máquinas virtuales activas
        Argumentos:
            Ninguna
        Devuelve:
            Una lista con los identificadores únicos de las máquinas virtuales activas.
        """
        query = "SELECT CommandID FROM ActiveDomainUIDs;"
        rows = self._executeQuery(query, False)
        if (rows == None) :
            return []
        result = []
        for row in rows :
            result.append(row)
        return result
    
    def getRegisteredDomainNames(self):
        """
        Devuelve una lista con los nombres de los dominios activos.
        Argumentos:
            Ninguno
        Devuelve:
            Lisa de strings con los nombres de los dominios activos.
        """
        query = "SELECT domainName FROM ActualVM;"
        results = self._executeQuery(query, False)
        if (results == None) :
            return []
        else :
            ac = []
            for row in results:
                ac.append(row)
            return ac
        
    def allocateAssignedMACsUUIDsAndVNCPorts(self):
        """
        Marca como utilizadas las MACs y los UUIDs de las máquinas virtuales activas
        en el arranque del servidor.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        assignedMACs, assignedVNCPorts = self.__getAssignedResources()
        for macAddress in assignedMACs :
            self.__allocateMACAddressAndUUID(macAddress)
        for port in assignedVNCPorts :
            self.__allocatePort(port)
        
    def addToTransferQueue(self, data):
        """
        Añade una petición a la cola de transferencias
        Argumentos:
            data: un diccionario con los datos de la petición a añadir
        Devuelve:
            Nada
        """
        serialized_data = ""
        serialized_data += str(data["Transfer_Type"]) + "$"
        serialized_data += data["RepositoryIP"] + "$"
        serialized_data += str(data["RepositoryPort"]) + "$"
        serialized_data += data["CommandID"] + "$"
        if (data["Transfer_Type"] == TRANSFER_T.STORE_IMAGE) :
            serialized_data += str(data["TargetImageID"]) + "$"
            serialized_data += data["SourceFilePath"]
        elif (data["Transfer_Type"] != TRANSFER_T.CANCEL_EDITION) :        
            serialized_data += str(data["SourceImageID"]) + "$"
            if (data["Transfer_Type"] == TRANSFER_T.CREATE_IMAGE or data["Transfer_Type"] == TRANSFER_T.EDIT_IMAGE) :    
                serialized_data += str(data["UserID"])
        else :
            serialized_data += str(data["ImageID"])
        
        
        insert = "INSERT INTO TransferQueue(data) VALUES ('{0}');".format(serialized_data)
        self._executeUpdate(insert)  

    def peekFromTransferQueue(self):
        """
        Lee el primero elemento (sin eliminarlo) de la cola de transferencias.
        Argumentos:
            Ninguno
        Devuelve:
            Un diccionario con los datos de la transferencia leída. Si la cola está vacía, devuelve
            None
        """
        query = "SELECT MIN(position) FROM TransferQueue;"
        first_element_ID = self._executeQuery(query, True)
        if (first_element_ID == None) :
            return None
        query = "SELECT data FROM TransferQueue WHERE position = {0};".format(first_element_ID)
        serialized_data = self._executeQuery(query, True)
        tokens = serialized_data.split("$")
        result = dict()
        result["Transfer_Type"] = int(tokens[0]) 
        result["RepositoryIP"] = tokens[1]
        result["RepositoryPort"] = int(tokens[2])
        result["CommandID"] = tokens[3]
        if (result["Transfer_Type"] == TRANSFER_T.STORE_IMAGE) :
            result["TargetImageID"] = int(tokens[4])
            result["SourceFilePath"] = tokens[5]           
        elif (result["Transfer_Type"] != TRANSFER_T.CANCEL_EDITION) :   
            result["SourceImageID"] = int(tokens[4])
            if (result["Transfer_Type"] == TRANSFER_T.CREATE_IMAGE or result["Transfer_Type"] == TRANSFER_T.EDIT_IMAGE) :             
                result["UserID"] = int(tokens[5])
        else :
            result["ImageID"] = int(tokens[4])
        return result
        
    def removeFirstElementFromTransferQueue(self):
        """
        Elimina la cabecera de la cola de transferencias.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        query = "SELECT MIN(position) FROM TransferQueue;"
        first_element_ID = self._executeQuery(query, True)
        if (first_element_ID == None) :
            return
        else :
            first_element_ID = first_element_ID
        update = "DELETE FROM TransferQueue WHERE position = {0};".format(first_element_ID)
        self._executeUpdate(update)
    
    def addToCompressionQueue(self, data):
        serialized_data = ""
        serialized_data += str(data["Transfer_Type"]) + "$"
        serialized_data += data["CommandID"] + "$"
        serialized_data += str(data["TargetImageID"]) + "$"
        serialized_data += data["RepositoryIP"] + "$"
        serialized_data += str(data["RepositoryPort"]) + "$"
        if (data["Transfer_Type"] == TRANSFER_T.STORE_IMAGE) :
            serialized_data += data["OSImagePath"] + "$"
            serialized_data += data["DataImagePath"] + "$"
            serialized_data += data["DefinitionFilePath"] + "$"            
        else :
            serialized_data += str(data["SourceImageID"]) 
            if (data["Transfer_Type"] != TRANSFER_T.DEPLOY_IMAGE) :            
                serialized_data += "$" + str(data["UserID"])
            
        insert = "INSERT INTO CompressionQueue(data) VALUES ('{0}');".format(serialized_data)
        self._executeUpdate(insert)  
            
    def peekFromCompressionQueue(self):
        query = "SELECT MIN(position) FROM CompressionQueue;"
        first_element_ID = self._executeQuery(query, True)
        if (first_element_ID == None) :
            return None
        query = "SELECT data FROM CompressionQueue WHERE position = {0};".format(first_element_ID)
        serialized_data = self._executeQuery(query, True)
        tokens = serialized_data.split("$")
        result = dict()
        result["Transfer_Type"] = int(tokens[0])
        result["CommandID"] = tokens[1]
        result["TargetImageID"] = int(tokens[2])
        result["RepositoryIP"] = tokens[3]
        result["RepositoryPort"] = int(tokens[4])
        if (result["Transfer_Type"] == TRANSFER_T.STORE_IMAGE) :
            result["OSImagePath"] = tokens[5]
            result["DataImagePath"] = tokens[6]
            result["DefinitionFilePath"] = tokens[7]            
        else:
            result["SourceImageID"] = int(tokens[5])
            if (result["Transfer_Type"] != TRANSFER_T.DEPLOY_IMAGE) :
                result["UserID"] = int(tokens[6])
            
        return result
            
    def removeFirstElementFromCompressionQueue(self):
        """
        Elimina la cabecera de la cola de transferencias.
        Argumentos:
            Ninguno
        Devuelve:
            Nada
        """
        query = "SELECT MIN(position) FROM CompressionQueue;"
        first_element_ID = self._executeQuery(query, True)
        if (first_element_ID == None) :
            return
        update = "DELETE FROM CompressionQueue WHERE position = {0};".format(first_element_ID)
        self._executeUpdate(update)
    
    def addValueToConnectionDataDictionary(self, commandID, value):
        serialized_data = value["RepositoryIP"] + "$" + str(value["RepositoryPort"])
        update = "INSERT INTO ConnectionDataDictionary VALUES('{0}', '{1}');".format(commandID, serialized_data)
        self._executeUpdate(update)
        
    def getImageRepositoryConnectionData(self, commandID):
        query = "SELECT value FROM ConnectionDataDictionary WHERE dict_key = '{0}';".format(commandID)
        result = self._executeQuery(query)
        if (result == None) :
            return None
        else:
            result = result[0]
        value = dict()
        tokens = result.split("$")
        value["RepositoryIP"] = tokens[0]
        value["RepositoryPort"] = int(tokens[1])
        return value
    
    def removeImageRepositoryConnectionData(self, commandID):
        update = "DELETE FROM ConnectionDataDictionary WHERE dict_key = '{0}';".format(commandID)
        self._executeUpdate(update)        