# -*- coding: UTF8 -*-
import MySQLdb


class RuntimeData(object):
    '''
        Esta clase se encargará de gestionar las características de las diferentes 
         máquinas virtuales que se encuentran en ejecución en un momento determinado.
         Además también se encargará de registrar en la base de datos las nuevas máquinas 
         virtuales en ejecución y de dar de baja aquellas máquinas que se apaguen.
    '''
    def __init__(self,sqlUser,sqlPass,databaseName):
        '''
            Constructora de la clase
        '''
        #Guardamos los atributos de conexión necesarios
        self.__sqlUser = sqlUser
        self.__sqlPass = sqlPass
        self.__databaseName = databaseName
        # Nos conectamos a MySql 
        self.__db = self.connect()
        self.__cursor = self.__db.cursor()
        #Llamamos a la función encargada de generar las MACS
        self.generateInitMacsAndUuids()
        self.generateVNCPorts()
        
    def generateInitMacsAndUuids(self): 
        '''
            Función encargada de crear la tabla inicial de pares (UUID,MAC) libres
        '''
        sql = "DROP TABLE IF EXISTS freeMacs" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)  
        #Creamos la tabla necesaria
        sql = "CREATE TABLE IF NOT EXISTS freeMacs(UUID VARCHAR(40) ,MAC VARCHAR(20),PRIMARY KEY(UUID,MAC))"
        #Ejecutamos el comando
        self.__cursor.execute(sql)
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
            self.__cursor.execute(sql)
            #incrementamos el contador
            v = v + 1
            
        #Actualizamos la base de datos
        self.__db.commit() 
        
    def generateVNCPorts(self): 
        '''
            Función encargada de crear la tabla inicial de pares (UUID,MAC) libres
        '''
        sql = "DROP TABLE IF EXISTS freeVNCPorts" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)  
        #Creamos la tabla necesaria
        sql = "CREATE TABLE IF NOT EXISTS freeVNCPorts(VNCPort INTEGER PRIMARY KEY)"
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Generamos el relleno
        p = 15000
        v = 0
        #Generamos el bucle
        while v < 256 :
            #Creamos la consulta   
            sql = "INSERT INTO freeVNCPorts VALUES ('" + str(p) + "');"
            #Ejecutamos el comando
            self.__cursor.execute(sql)
            #incrementamos el contador
            p = p + 2
            v = v + 1
            
        #Actualizamos la base de datos
        self.__db.commit() 
        
    def extractfreeMacAndUuid(self):
        '''
            Función que devuelve la primera ocurrencia de la tabla de macs libres y
             la elimina de la tabla
        '''
        #Creamos la cosulta
        sql = "SELECT * FROM freeMacs"
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Nos quedamos con la primera ocurrencia
        result=self.__cursor.fetchone()
        
        #Eliminamos este resultado de la tabla
        sql = "DELETE FROM freeMacs WHERE UUID = '" + result[0] + "' AND MAC ='" + result[1] + "'"
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Gracias al ON DELETE CASCADE se borrarán las imagenes registradas para este servidor
        #Actualizamos la base de datos
        self.__db.commit() 
        
        #Devolvemos una tupla con la UUID y la MAC
        return (result[0],result[1])
    
    def insertfreeMacAndUuid(self,UUID,MAC):
        '''
            Añade un nuevo par del tipo UUID , MAC a la tabla freeMAC
        '''
        #Creamso la consulta
        sql = "INSERT INTO freeMacs VALUES ('" + UUID +"','" + MAC + "')"
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Actualizamos la base de datos
        self.__db.commit() 
        
    def extractfreeVNCPort(self):
        '''
            Función que devuelve la primera ocurrencia de la tabla de macs libres y
             la elimina de la tabla
        '''
        #Creamos la cosulta
        sql = "SELECT * FROM freeVNCPorts"
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Nos quedamos con la primera ocurrencia
        result=self.__cursor.fetchone()
        
        #Eliminamos este resultado de la tabla
        sql = "DELETE FROM freeVNCPorts WHERE VNCPort = '" + str(result[0]) + "'"
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Gracias al ON DELETE CASCADE se borrarán las imagenes registradas para este servidor
        #Actualizamos la base de datos
        self.__db.commit() 
        
        #Devolvemos el puerto
        return result[0]
    
    def insertfreeVNCPort(self,VNCPort):
        '''
            Añade un nuevo par del tipo UUID , MAC a la tabla freeMAC
        '''
        #Creamso la consulta
        sql = "INSERT INTO freeVNCPorts VALUES ('" + str(VNCPort) + "')"
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Actualizamos la base de datos
        self.__db.commit() 
        
        
    def connect(self):
        '''
            Establece la conexión con MySql
        '''
        # Nos conectamos a MySql 
        db=MySQLdb.connect(host='localhost',user= self.__sqlUser,passwd= self.__sqlPass)
        cursor=db.cursor()
        #Cambiamos a la base de datos indicada
        sql = "USE " + self.__databaseName     
        #Ejecutamos el comando
        cursor.execute(sql)
        #devolvemos el cursor
        return db
    
    def disconnect(self):
        '''
            Cierra la conexión con MySql
        '''
        #cerramos las conexiones
        self.__cursor.close()
        self.__db.close()
        
    def showVMs(self):
        '''
            Muestra el conjunto de MV registradas
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT * FROM ActualVM" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        results=self.__cursor.fetchall()
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
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        results=self.__cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        ports = []
        for r in results:
            ports.append(r[0])
        #Devolvemos la lista resultado
        return ports
    
    def getUsers(self):
        '''
             Devuelve una lista con los identificadores de todos los usuarios que actualmente
               se encuentran ejecutando una determinada máquina virtual en este servidor de 
               máquinas virtuales.
        ''' 
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT userId FROM ActualVM" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        results=self.__cursor.fetchall()
        #Guardamos en una lista los ids resultantes
        users = []
        for r in results:
            users.append(r[0])
        #Devolvemos la lista resultado
        return users
    
    def getAssignedVM(self,vncPort):
        '''
            Devuelve el identificador de la máquina virtual que se encuentra en ejecución en el 
             puerto VNC pasado como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VMId FROM ActualVM WHERE VNCPortAdress = '" + str(vncPort) + "'" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos el resultado
        result=self.__cursor.fetchone()
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
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos el resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0] 
    
    def getMachineDataPath(self,vncPort):
        '''
            Devuelve la ruta asociada a la copia de la imagen de la máquina virtual que se encuentra 
             en ejecución en el puertoVNC pasado como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT imageCopyPath FROM ActualVM  WHERE VNCPortAdress = '" + str(vncPort) + "'"
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos el resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0] 
    
    def getMacAdress(self,vncPort):
        '''
            Devuelve la dirección MAC del cliente VNC cuyo puerto se pasa como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT macAdress FROM ActualVM WHERE VNCPortAdress = '" + str(vncPort) + "'" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos el resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0] 
    
    def getUuidAdress(self,vncPort):
        '''
            Devuelve la uuid del cliente VNC cuyo puerto se pasa como argumento.
        '''
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT uuid FROM ActualVM WHERE VNCPortAdress = '" + str(vncPort) + "'" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos el resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0] 
    
    def getPassword(self,vncPort): 
        '''
            Devuelve la contraseña que se ha dado al puerto VNC que se le pasa como argumento.
        ''' 
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VNCPass FROM ActualVM WHERE VNCPortAdress = '" + str(vncPort) + "'" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos el resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0]
    
    def getVMPid(self,vncPort): 
        '''
            Devuelve la contraseña que se ha dado al puerto VNC que se le pasa como argumento.
        ''' 
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT VMPid FROM ActualVM WHERE VNCPortAdress = '" + str(vncPort) + "'" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos el resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0]
    
    def getOsImagePath(self,vncPort): 
        '''
            Devuelve la contraseña que se ha dado al puerto VNC que se le pasa como argumento.
        ''' 
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT osImagePath FROM ActualVM WHERE VNCPortAdress = '" + str(vncPort) + "'" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos el resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0]
    
    def getDomainName(self,vncPort): 
        '''
            Devuelve la contraseña que se ha dado al puerto VNC que se le pasa como argumento.
        ''' 
        #Creamos la consulta encargada de extraer los datos
        sql = "SELECT domainName FROM ActualVM WHERE VNCPortAdress = '" + str(vncPort) + "'" 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos el resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        return result[0]
    
    def registerVMResources(self,vncPort,userId, VMId, VMPid, imageCopyPath,osImagePath,mac,uuid, password):
        '''
            Permite dar de alta una nueva máquina virtual en ejecución cuyas características se pasan
             como argumentos.
        '''
        ##Buscamos el nombre de la máquina virtual
        sql = "SELECT name FROM VirtualMachine WHERE VMId = " + str(VMId) 
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos el resultado
        result=self.__cursor.fetchone()
        #Devolvemos el resultado
        VMName = result[0]
        #Formamos el nombre del dominio
        domainName = VMName + str(vncPort) 
        
        #CInsertamos los datos nuevos en la BD
        sql = "INSERT INTO ActualVM VALUES('"  + domainName + "'," 
        sql+=    str(VMId) + "," + str(userId)  +"," + str(vncPort) +"," + str(VMPid) + ",'"  
        sql +=  imageCopyPath + "','" + osImagePath + "','" + mac + "','" + uuid + "','"
        sql +=  password + "')"  
        #Ejecutamos el comando
        self.__cursor.execute(sql)  
        #Actualizamos la base de datos
        self.__db.commit()              
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
        self.__cursor.execute(sql)
        #Gracias al ON DELETE CASCADE se borrarán las imagenes registradas para este servidor
        #Actualizamos la base de datos
        self.__db.commit() 
        
    def isVMExists(self,port):   
        '''
            Comprueba si una imagen existe
        '''
        #Contamos el número de máquinas virtuales asociadas al puerto VNC dado     
        sql = "SELECT COUNT(*) FROM ActualVM WHERE VNCPortAdress =" + str(port)
        #Ejecutamos el comando
        self.__cursor.execute(sql)
        #Recogemos los resultado
        result=self.__cursor.fetchone()
        #Si el resultado es 1, la MV existirá
        return (result[0] == 1) 
        
def main():    
    #Instanciamos la clase
    runtimeData = RuntimeData("CygnusCloud","cygnuscloud2012","DBVMServer")
    #Comenzamos con las pruebas
    other = 's'
    while(other == 's'):
        print("Escoja un numero de prueba (1-15)")
        prueba = raw_input()
        
        if(prueba == '1'):
            #Puertos VNC actualmente en uso
            print("Prueba 1")
            print("Las VM actualmente en uso son:")
            ports = runtimeData.getRunningPorts()
            for p in ports:
                print(p)
        elif(prueba == '2'):
            #usuarios actuales
            print("Prueba 2")
            print("Los usuarios con máquinas virtuales actualmente activas son:")
            users = runtimeData.getUsers()
            for u in users:
                print(u)
        elif(prueba == '3'):
            #MV asociado a un puerto
            print("Prueba 3")
            print("Indique el identificador del puerto")
            port = raw_input()
            VMId = runtimeData.getAssignedVM(port)
            print("La máquina virtual asociada a este puerto es:")
            print(VMId)
        elif(prueba == '4'):
            #nombre de la MV asociado a un puerto
            print("Prueba 4")
            print("Indique el identificador del puerto")
            port = raw_input()
            VMName = runtimeData.getAssignedVMName(port)
            print("La máquina virtual asociada a este puerto es:")
            print(VMName)
        elif(prueba == '5'):
            #ruta de la MV asociado a un puerto
            print("Prueba 5")
            print("Indique el identificador del puerto")
            port = raw_input()
            path = runtimeData.getMachineDataPath(port)
            print("La ruta de la máquina virtual asociada a este puerto es:")
            print(path)
        elif(prueba == '6'):
            #direccion MAC asociado a un puerto
            print("Prueba 6")
            print("Indique el identificador del puerto")
            port = raw_input()
            mac = runtimeData.getMacAdress(port)
            print("La dirección MAC asociada a este puerto es:")
            print(mac)
        elif(prueba == '7'):
            #contraseña asociado a un puerto
            print("Prueba 7")
            print("Indique el identificador del puerto")
            port = raw_input()
            password = runtimeData.getPassword(port)
            print("La contraseña asociada a este puerto es:")
            print(password)
        elif(prueba == '8'):
            #registro de una nueva MV
            print("Prueba 8")
            print("Indique el identificador del puerto")
            port = raw_input()
            print("Indique el identificador del usuario")
            userId = raw_input()
            print("Indique el identificador de la MV")
            vmId = raw_input()
            print("Indique el PID")
            pid = raw_input()
            print("Indique la ruta")
            path = raw_input()
            print("Indique la ruta del OS")
            osPath = raw_input()
            print("Indique la direccion MAC")
            mac = raw_input()
            print("Indique la uuid")
            uuid = raw_input()
            print("Indique la contraseña")
            portPass = raw_input()
            
            portId = runtimeData.registerVMResources(port,userId,vmId, pid, path, osPath, mac, uuid, portPass)
            print("MV registrada:")
            runtimeData.showVMs()
        elif(prueba == '9'):
            #borrado de una máquina virtual
            print("Prueba 9")
            print("Indique el nombre del dominio del puerto a dar de baja")
            domainName = raw_input()
            runtimeData.unRegisterVMResources(domainName)
            print("La máquina virtual ha sido dada de baja:")
            runtimeData.showVMs()
        elif(prueba == '10'):
            #extracción de una MAC libre
            print("Prueba 10")
            print("La proxima MAC libre es:")
            (uuid,mac) = runtimeData.extractfreeMacAndUuid()
            print("UUID = " + uuid)
            print("MAC = " + mac)
        elif(prueba == '11'):
            #Adición de una MAC a la lista libre
            print("Prueba 11")
            print("Indique el UUID:")
            uuid = raw_input()
            print("Indique la direccion MAC:")
            mac = raw_input()
            runtimeData.insertfreeMacAndUuid(uuid, mac)
            print("La nueva MAC ha sido añadida")
            
        elif(prueba == '12'):
            #contraseña asociado a un puerto
            print("Prueba 12")
            print("Indique el identificador del puerto")
            port = raw_input()
            pid = runtimeData.getVMPid(port)
            print("El PID asociado a este puerto es:")
            print(pid)
            
        elif(prueba == '13'):
            #contraseña asociado a un puerto
            print("Prueba 13")
            print("Indique el identificador del puerto")
            port = raw_input()
            osImagePath = runtimeData.getOsImagePath(port)
            print("La ruta del OS asociado a este puerto es:")
            print(osImagePath)
            
        elif(prueba == '14'):
            #extracción de una MAC libre
            print("Prueba 10")
            print("La proxima VNCPort libre es:")
            VNCPort = runtimeData.extractfreeVNCPort()
            print("Puerto = " + str(VNCPort))
            
        elif(prueba == '15'):
            #Adición de una MAC a la lista libre
            print("Prueba 11")
            print("Indique el puerto:")
            VNCPort = raw_input()
            runtimeData.insertfreeVNCPort(VNCPort)
            print("El nuevo puerto ha sido añadida")
        elif(prueba == '16'):
             #contraseña asociado a un puerto
            print("Prueba 16")
            print("Indique el identificador del puerto")
            port = raw_input()
            domainName = runtimeData.getDomainName(port)
            print("El nombre del dominio asociado a este puerto es:")
            print(domainName)           
        else:
            print("Prueba no disponible.")
               
        #Comprobamos si se quiere hacer otra prueba
        print("Desea hacer otra prueba?(s/n)")
        other = raw_input() 
         
    #Nos desconectamos
    runtimeData.disconnect()

## Comandos a ejecutar de inicio (solo en caso de pruebas)
if __name__ == "__main__":
    main()                        