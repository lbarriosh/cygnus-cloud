# -*- coding: UTF8 -*-
from database.utils.connector import BasicDatabaseConnector

class VMServerDBConnector(BasicDatabaseConnector):
    '''
        Esta clase permite gestionar las diferentes características de las imágenes 
         accesibles en el servidor de máquinas virtuales actual.
    '''

    def __init__(self,sqlUser,sqlPass,databaseName):
        '''
            Constructora de la clase
        '''
        BasicDatabaseConnector.__init__(self, sqlUser, sqlPass, databaseName)
        self.connect()
        self.generateMACsAndUUIDs()
        self.generateVNCPorts()
        
    def getImages(self):
        '''
             Devuelve una lista con todos los identificadores de imágenes que se 
              encuentran registradas en el servidor de máquinas virtuales.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VMId FROM VirtualMachine" 
        #Recogemos los resultado
        results=self._executeQuery(sql, False)
        #Guardamos en una lista los ids resultantes
        imageIds = []
        for r in results:
            imageIds.append(r[0])
        #Devolvemos la lista resultado
        return imageIds
    
    def getName(self,imageId):
        '''
            Devuelve el nombre de la imagen cuyo identificador se pasa como argumento. 
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT name FROM VirtualMachine WHERE VMId = " + str(imageId)   
        #Recogemos los resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0]  
    
    def getImagePath(self,imageId):
        '''
            Devuelve la ruta donde se encuentra físicamente la imagen cuyo identificador 
             de imagen se pasa como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT imagePath FROM VirtualMachine WHERE VMId = " + str(imageId)   
        #Recogemos los resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0]
    
    def getOsImagePathFromImageId(self,imageId):
        '''
            Devuelve la ruta donde se encuentra físicamente la imagen del SO cuyo identificador 
             de imagen se pasa como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT osImagePath FROM VirtualMachine WHERE VMId = " + str(imageId)   
        #Recogemos los resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0]
    
    def getFileConfigPath(self,imageId):
        '''
            Devuelve la ruta donde se encuentra el fichero de configuración asociado a 
             la imagen cuyo identificador se pasa como argumento
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT FileConfigPath FROM VirtualMachine WHERE VMId = " + str(imageId)   
        #Recogemos los resultado
        result=self._executeQuery(sql)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0][0] # BUG aquí
    
    def setImagePath(self,imageId,path):
        '''
            Permite cambiar la ruta de la imagen cuyo identificador se pasa como argumento.
        '''
        #Creamos la consulta encargada de realizar la actualización
        sql = "UPDATE VirtualMachine SET imagePath = '"  + path + "' WHERE VMId = " + str(imageId)
        #Ejecutamos el comando
        self._executeUpdate(sql)
        
    def createImage(self,imageId,name,imagePath,osImagePath,FileConfigPath):
        '''
            Permite registrar en la base de datos una nueva imagen de máquina virtual. 
        '''
        #Introducimos los datos en la base de datos
        sql = "INSERT INTO VirtualMachine(VMId,name,imagePath,osImagePath,FileConfigPath) VALUES("  
        sql+=    str(imageId) + ",'" + name + "','" + imagePath  +"','" + osImagePath + "','"+ FileConfigPath +"') "  
        #Ejecutamos el comando
        self._executeUpdate(sql)  
        #Devolvemos el id
        return imageId
    
    def deleteImage(self,imageId):
        #borramos el la MV
        sql = "DELETE FROM VirtualMachine WHERE VMId =" + str(imageId) 
        #Ejecutamos el comando
        self._executeUpdate(sql) 
        # Gracias al ON DELETE CASCADE debería borrarse sus referencias en
        #  el resto de las tablas
        #Actualizamos la base de datos
 
    def doesImageExist(self,VMId):   
        '''
            Comprueba si una imagen existe
        '''
        #Contamos el número de MV con el id dado    
        sql = "SELECT COUNT(*) FROM VirtualMachine WHERE VMId =" + str(VMId)
        #Recogemos los resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        # Si el resultado es 1, la MV existe
        return (result[0] == 1)
    
    def generateMACsAndUUIDs(self): 
        '''
            Función encargada de crear la tabla inicial de pares (UUID,MAC) libres
        '''
        sql = "DROP TABLE IF EXISTS freeMacs" 
        #Ejecutamos el comando
        self._executeUpdate(sql)  
        #Creamos la tabla necesaria
        sql = "CREATE TABLE IF NOT EXISTS freeMacs(UUID VARCHAR(40) ,MAC VARCHAR(20),PRIMARY KEY(UUID,MAC)) ENGINE=MEMORY;"
        #Ejecutamos el comando
        self._executeUpdate(sql)
        #Generamos el relleno
        v = 0
        #Generamos el bucle
        while v < 256 :
            x = str(hex(v))[2:].upper()
            #Ajustamos al formato de 2 digitos cuando proceda
            if v < 16:
                x = '0' + x
            #Creamos la consulta   
            sql = "INSERT INTO freeMacs VALUES (UUID(),'" + '2C:00:00:00:00:' +  x + "');"
            #Ejecutamos el comando
            self._executeUpdate(sql)
            #incrementamos el contador
            v = v + 1
            
        
    def generateVNCPorts(self): 
        '''
            Función encargada de crear la tabla inicial de pares (UUID,MAC) libres
        '''
        sql = "DROP TABLE IF EXISTS freeVNCPorts;" 
        #Ejecutamos el comando
        self._executeUpdate(sql)  
        #Creamos la tabla necesaria
        sql = "CREATE TABLE IF NOT EXISTS freeVNCPorts(VNCPort INTEGER PRIMARY KEY) ENGINE=MEMORY;"
        #Ejecutamos el comando
        self._executeUpdate(sql)
        #Generamos el relleno
        p = 15000
        v = 0
        #Generamos el bucle
        while v < 256 :
            #Creamos la consulta   
            sql = "INSERT INTO freeVNCPorts VALUES ('" + str(p) + "');"
            #Ejecutamos el comando
            self._executeUpdate(sql)
            #incrementamos el contador
            p = p + 2
            v = v + 1
        
    def extractfreeMacAndUuid(self):
        '''
            Función que devuelve la primera ocurrencia de la tabla de macs libres y
             la elimina de la tabla
        '''
        #Creamos la cosulta
        sql = "SELECT * FROM freeMacs"
        #Nos quedamos con la primera ocurrencia
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None        
        #Eliminamos este resultado de la tabla
        sql = "DELETE FROM freeMacs WHERE UUID = '" + result[0] + "' AND MAC ='" + result[1] + "'"
        #Ejecutamos el comando
        self._executeUpdate(sql)
        #Gracias al ON DELETE CASCADE se borrarán las imagenes registradas para este servidor
        #Actualizamos la base de datos
        
        #Devolvemos una tupla con la UUID y la MAC
        return (result[0],result[1])
    
    def insertfreeMacAndUuid(self,UUID,MAC):
        '''
            Añade un nuevo par del tipo UUID , MAC a la tabla freeMAC
        '''
        #Creamso la consulta
        sql = "INSERT INTO freeMacs VALUES ('" + UUID +"','" + MAC + "')"
        #Ejecutamos el comando
        self._executeUpdate(sql)
        
    def extractfreeVNCPort(self):
        '''
            Función que devuelve la primera ocurrencia de la tabla de macs libres y
             la elimina de la tabla
        '''
        #Creamos la cosulta
        sql = "SELECT * FROM freeVNCPorts"
        #Nos quedamos con la primera ocurrencia
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Eliminamos este resultado de la tabla
        sql = "DELETE FROM freeVNCPorts WHERE VNCPort = '" + str(result[0]) + "'"
        #Ejecutamos el comando
        self._executeUpdate(sql)
        #Gracias al ON DELETE CASCADE se borrarán las imagenes registradas para este servidor
        #Actualizamos la base de datos
        
        #Devolvemos el puerto
        return result[0]
    
    def insertfreeVNCPort(self,VNCPort):
        '''
            Añade un nuevo par del tipo UUID , MAC a la tabla freeMAC
        '''
        #Creamso la consulta
        sql = "INSERT INTO freeVNCPorts VALUES ('" + str(VNCPort) + "')"
        #Ejecutamos el comando
        self._executeUpdate(sql)
        
    def showVMs(self):
        '''
            Muestra el conjunto de MV registradas
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT * FROM ActualVM" 
        #Recogemos los resultado
        results=self._executeQuery(sql, False)
        #Mostramos los resultados
        for r in results:
            print(r)        
        

    def getRunningPorts(self):
        '''
            Devuelve una lista con los puertos VNC correspondientes a las máquinas 
             virtuales que se encuentran actualmente en ejecución.
        ''' 
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VNCPortAdress FROM ActualVM" 
        #Recogemos los resultado
        results=self._executeQuery(sql, False)
        #Guardamos en una lista los ids resultantes
        ports = []
        for r in results:
            ports.append(int(r[0]))
        #Devolvemos la lista resultado
        return ports
    
    def getUsers(self):
        '''
             Devuelve una lista con los identificadores de todos los usuarios que actualmente
               se encuentran ejecutando una determinada máquina virtual en este servidor de 
               máquinas virtuales.
        ''' 
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT DISTINCT userId FROM ActualVM;" 
        #Recogemos los resultado
        results=self._executeQuery(sql, False)
        #Guardamos en una lista los ids resultantes
        users = []
        for r in results:
            users.append(int(r[0]))
        #Devolvemos la lista resultado
        return users
    
    def getAssignedVM(self,vncPort):
        '''
            Devuelve el identificador de la máquina virtual que se encuentra en ejecución en el 
             puerto VNC pasado como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VMId FROM ActualVM WHERE VNCPortAdress = '" + str(vncPort) + "'" 
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0] 
    
    def getAssignedVMinDomain(self,domainName):
        '''
            Devuelve el identificador de la máquina virtual que se encuentra en ejecución en el 
            dominio pasado como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VMId FROM ActualVM WHERE domainName = '" + str(domainName) + "'" 
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0] 
    
    def getAssignedVMName(self,vncPort):
        '''
            Devuelve el nombre de la máquina virtual que se encuentra en ejecución
             en  el puerto VNC pasado como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT vm.name FROM ActualVM av,VirtualMachine vm WHERE av.VNCPortAdress = '" + str(vncPort) + "' AND "
        sql += "vm.VMId = av.VMId " 
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0] 
    
    def getAssignedVMNameinDomain(self,domainName):
        '''
            Devuelve el nombre de la máquina virtual que se encuentra en ejecución
             en  el puerto VNC pasado como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT vm.name FROM ActualVM av,VirtualMachine vm WHERE av.domainName = '" + str(domainName) + "' AND "
        sql += "vm.VMId = av.VMId " 
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0] 
    
    def getMachineDataPath(self,vncPort):
        '''
            Devuelve la ruta asociada a la copia de la imagen de la máquina virtual que se encuentra 
             en ejecución en el puertoVNC pasado como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT imageCopyPath FROM ActualVM  WHERE VNCPortAdress = '" + str(vncPort) + "'"
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0] 
    
    def getMachineDataPathinDomain(self,domainName):
        '''
            Devuelve la ruta asociada a la copia de la imagen de la máquina virtual que se encuentra 
             en ejecución en el puertoVNC pasado como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT imageCopyPath FROM ActualVM  WHERE domainName = '" + str(domainName) + "'"
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0] 
    
    def getMacAdress(self,vncPort):
        '''
            Devuelve la dirección MAC del cliente VNC cuyo puerto se pasa como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT macAdress FROM ActualVM WHERE VNCPortAdress = '" + str(vncPort) + "'" 
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0] 
    
    def getMacAdressinDomain(self,domainName):
        '''
            Devuelve la dirección MAC del cliente VNC cuyo puerto se pasa como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT macAdress FROM ActualVM WHERE domainName = '" + str(domainName) + "'" 
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0] 
    
    def getUuidAdress(self,vncPort):
        '''
            Devuelve la uuid del cliente VNC cuyo puerto se pasa como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT uuid FROM ActualVM WHERE VNCPortAdress = '" + str(vncPort) + "'" 
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0] 
    
    def getUuidAdressInDomain(self,domainName):
        '''
            Devuelve la uuid del cliente VNC cuyo puerto se pasa como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT uuid FROM ActualVM WHERE domainName = '" + str(domainName) + "'" 
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0] 
    
    def getPassword(self,vncPort): 
        '''
            Devuelve la contraseña que se ha dado al puerto VNC que se le pasa como argumento.
        ''' 
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VNCPass FROM ActualVM WHERE VNCPortAdress = '" + str(vncPort) + "'" 
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0]
    
    def getPasswordinDomain(self,domainName): 
        '''
            Devuelve la contraseña que se ha dado al puerto VNC que se le pasa como argumento.
        ''' 
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VNCPass FROM ActualVM WHERE domainName = '" + str(domainName) + "'" 
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0]
    
    def getVMPid(self,vncPort): 
        '''
            Devuelve la contraseña que se ha dado al puerto VNC que se le pasa como argumento.
        ''' 
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VMPid FROM ActualVM WHERE VNCPortAdress = '" + str(vncPort) + "'" 
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0]
    
    def getVMPidinDomain(self,domainName): 
        '''
            Devuelve la contraseña que se ha dado el dominio que se le pasa como argumento.
        ''' 
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VMPid FROM ActualVM WHERE domainName = '" + str(domainName) + "'" 
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0] 
    
    
    def getOsImagePathinDomain(self,domainName): 
        '''
            Devuelve la contraseña que se ha dado al dominio que se le pasa como argumento.
        ''' 
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT osImagePath FROM ActualVM WHERE domainName = '" + str(domainName) + "'" 
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0]    
    
    def getDomainName(self,vncPort): 
        '''
            Devuelve la contraseña que se ha dado al puerto VNC que se le pasa como argumento.
        ''' 
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT domainName FROM ActualVM WHERE VNCPortAdress = '" + str(vncPort) + "'" 
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return result[0]
    
    def registerVMResources(self,domainName,vncPort,userId, VMId, VMPid, imageCopyPath,osImagePath,mac,uuid, password):
        '''
            Permite dar de alta una nueva máquina virtual en ejecución cuyas características se pasan
             como argumentos.
        '''
        
        #CInsertamos los datos nuevos en la BD
        sql = "INSERT INTO ActualVM VALUES('"  + domainName + "'," 
        sql+=    str(VMId) + "," + str(vncPort)  +"," + str(userId) +"," + str(VMPid) + ",'"  # BUG: puerto e ID del usuario estaban intercambiados
        sql +=  imageCopyPath + "','" + osImagePath + "','" + mac + "','" + uuid + "','"
        sql +=  password + "')"  
        #Ejecutamos el comando
        self._executeUpdate(sql)        
        #devolvemos el puerto en el que ha sido creado
        return vncPort 
    
    def unRegisterVMResources(self,domainName):
        '''
            Da de baja en la base de datos el puerto VNC que se le pasa como argumento 
             y con él, todas las características asociadas al mismo.
        ''' 
        #Borramos la máquina virtual
        sql = "DELETE FROM ActualVM WHERE domainName = '" + str(domainName) + "'"
        #Ejecutamos el comando
        self._executeUpdate(sql)
        #Gracias al ON DELETE CASCADE se borrarán las imagenes registradas para este servidor
        #Actualizamos la base de datos
        
    def doesVMExist(self,port):   
        '''
            Comprueba si una imagen existe
        '''
        #Contamos el número de máquinas virtuales asociadas al puerto VNC dado     
        sql = "SELECT COUNT(*) FROM ActualVM WHERE VNCPortAdress =" + str(port)
        #Recogemos los resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Si el resultado es 1, la MV existirá
        return (result[0] == 1) 
    
    def getAssignedUserInDomain(self,domainName):
        '''
            Devuelve el identificador del usuario asociado a la mv que se encuentra en ejecución en el 
            dominio pasado como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT userId FROM ActualVM WHERE domainName = '" + str(domainName) + "'" 
        #Recogemos el resultado
        result=self._executeQuery(sql, True)
        if (result == None) : 
            return None
        #Devolvemos el resultado
        return int(result[0])
    
    def getVMsConnectionData(self):
        '''
        Devuelve una lista con los datos de conexión a las máquinas vituales activas
        Argumentos:
            Ninguno
        Devuelve:
            Lista de diccionarios con los datos de conexión a las máquinas virtuales
        '''
        query = "SELECT userId, VMId, domainName, VNCPortAdress, VNCPass FROM ActualVM;"
        results = self._executeQuery(query, False)
        if (results == None) :
            return []
        else :
            ac = []
            for row in results:
                ac.append({"UserID" : int(row[0]), "VMID" : int(row[1]), "VMName": row[2], "VNCPort" : int(row[3]), "VNCPass" : row[4]})
            return ac
        
    def addVMBootCommand(self, domainName, commandID):
        update = "INSERT INTO VMBootCommand VALUES ('" + domainName + "', '" + commandID + "');"
        self._executeUpdate(update)
        
    def getVMBootCommand(self, domainName):
        query = "SELECT commandID FROM VMBootCommand WHERE domainName = '" + domainName + "';"
        result = self._executeQuery(query, True)
        if (result == None) :
            return None
        update = "DELETE FROM VMBootCommand WHERE domainName = '" + domainName + "';"
        self._executeUpdate(update)
        return result[0]